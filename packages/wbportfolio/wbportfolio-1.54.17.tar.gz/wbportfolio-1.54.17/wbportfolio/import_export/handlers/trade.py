import math
from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from django.db import models
from wbcore.contrib.currency.import_export.handlers import CurrencyImportHandler
from wbcore.contrib.io.exceptions import DeserializationError
from wbcore.contrib.io.imports import ImportExportHandler
from wbfdm.import_export.handlers.instrument import InstrumentImportHandler
from wbfdm.models import InstrumentType

from wbportfolio.models.portfolio import Portfolio
from wbportfolio.models.products import update_outstanding_shares_as_task
from wbportfolio.utils import string_matching

from .register import RegisterImportHandler


class TradeImportHandler(ImportExportHandler):
    MODEL_APP_LABEL: str = "wbportfolio.Trade"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instrument_handler = InstrumentImportHandler(self.import_source)
        self.register_handler = RegisterImportHandler(self.import_source)
        self.currency_handler = CurrencyImportHandler(self.import_source)
        self.order_proposals = set()

    def _data_changed(self, _object, change_data: Dict[str, Any], initial_data: Dict[str, Any], **kwargs):
        if (new_register := change_data.get("register")) and (current_register := _object.register):
            # we replace the register only if the new one gives us more information
            if new_register.register_reference == current_register.global_register_reference:
                del change_data["register"]
        return super()._data_changed(_object, change_data, initial_data, **kwargs)

    def _deserialize(self, data: Dict[str, Any]):
        from wbportfolio.models import OrderProposal, Product

        if underlying_instrument := data.get("underlying_instrument", None):
            data["underlying_instrument"] = self.instrument_handler.process_object(
                underlying_instrument, only_security=False, read_only=True
            )[0]

        if order_proposal_id := data.pop("order_proposal_id", None):
            order_proposal = OrderProposal.objects.get(id=order_proposal_id)
            self.order_proposals.add(order_proposal)
            data["value_date"] = order_proposal.last_effective_date
            data["transaction_date"] = order_proposal.trade_date
            data["order_proposal"] = order_proposal
            data["portfolio"] = order_proposal.portfolio
            data["status"] = "DRAFT"
        else:
            if external_id_alternative := data.get("external_id_alternative", None):
                data["external_id_alternative"] = str(external_id_alternative)
            if transaction_date_str := data.get("transaction_date", None):
                data["transaction_date"] = datetime.strptime(transaction_date_str, "%Y-%m-%d").date()
            if value_date_str := data.get("value_date", None):
                data["value_date"] = datetime.strptime(value_date_str, "%Y-%m-%d").date()
            if book_date_str := data.get("book_date", None):
                data["book_date"] = datetime.strptime(book_date_str, "%Y-%m-%d").date()
            data["portfolio"] = Portfolio._get_or_create_portfolio(
                self.instrument_handler, data.get("portfolio", data["underlying_instrument"])
            )

            if currency_data := data.get("currency", None):
                data["currency"] = self.currency_handler.process_object(currency_data, read_only=True)[0]

            if register_data := data.get("register", None):
                data["register"] = self.register_handler.process_object(register_data)[0]

            data["marked_for_deletion"] = data.get("marked_for_deletion", False)
        if underlying_instrument := data.get("underlying_instrument"):
            if nominal := data.pop("nominal", None):
                try:
                    product = Product.objects.get(id=underlying_instrument.id)
                    data["shares"] = nominal / product.share_price
                except Product.DoesNotExist:
                    raise DeserializationError(
                        "We cannot compute the number of shares from the nominal value as we cannot find the product share price."
                    )
        else:
            raise DeserializationError("We couldn't find a valid underlying instrument this row.")

        for field in self.model._meta.get_fields():
            if not (value := data.get(field.name, None)) is None and isinstance(field, models.DecimalField):
                q = (
                    1 / (math.pow(10, 4))
                )  # we need that convertion mechanism otherwise there is floating point approximation error while casting to decimal and get_instance does not work as expected
                data[field.name] = Decimal(value).quantize(Decimal(str(q)))
        if (target_weight := data.pop("target_weight", None)) is not None:
            data["_target_weight"] = target_weight

    def _create_instance(self, data: Dict[str, Any], **kwargs) -> models.Model:
        if "transaction_date" not in data:  # we might get only book date and not transaction date
            data["transaction_date"] = data["book_date"]
        return self.model.objects.create(**data, import_source=self.import_source)

    def _get_instance(self, data: Dict[str, Any], history: Optional[models.QuerySet] = None, **kwargs) -> models.Model:
        self.import_source.log += "\nGet Trade Instance."
        if transaction_date := data.get("transaction_date"):
            dates_lookup = {"transaction_date": transaction_date}
        elif book_date := data.get("book_date"):
            dates_lookup = {"book_date": book_date}
        else:
            raise DeserializationError("date lookup is missing from data")
        self.import_source.log += f"\nParameter: Product={data['underlying_instrument']} Trade-Date={transaction_date} Shares={data.get('shares')} Weighting={data.get('weighting')}"

        if history.exists():
            queryset = history
        else:
            queryset = self.model.objects.filter(marked_for_deletion=False)

        queryset = queryset.filter(
            models.Q(underlying_instrument=data["underlying_instrument"]) & models.Q(**dates_lookup)
        )
        if "shares" in data:
            queryset = queryset.filter(shares=data["shares"])
        if _id := data.get("id", None):
            self.import_source.log += f"ID {_id} provided -> Load CustomerTrade"
            return self.model.objects.get(id=_id)
        # We need to check for external identifiers
        if external_id := data.get("external_id"):
            self.import_source.log += f"\nExternal Identifier used: {external_id}"
            external_id_queryset = queryset.filter(external_id=external_id)
            if external_id_queryset.count() == 1:
                self.import_source.log += f"External ID {external_id} provided -> Load CustomerTrade"
                return external_id_queryset.first()

        if portfolio := data.get("portfolio", None):
            queryset = queryset.filter(portfolio=portfolio)
        if queryset.exists():
            if bank := data.get("bank"):
                self.import_source.log += (
                    f"\n{queryset.count()} Trades found. The bank will tried to be matched against {bank}"
                )
                if queryset.filter(bank=bank).count() >= 1:  # exact match
                    queryset = queryset.filter(bank=bank)
                else:
                    best_result = string_matching(bank, queryset.values_list("bank", flat=True))
                    if best_result[1] >= 80:
                        possible_trades = queryset.filter(bank=best_result[0])
                        if possible_trades.count() > 1 and possible_trades.filter(claims__isnull=False).exists():
                            possible_trades = possible_trades.filter(claims__isnull=False)
                        if (
                            possible_trades.count() >= 1
                        ):  # If count is greater than 1, we get exact match so we return either trades
                            queryset = possible_trades
            if (queryset.count() > 1) and (price := data.get("price", None)):
                if queryset.filter(price=price).count() == 1:
                    queryset = queryset.filter(price=price)
            if queryset.exists():
                # We try to filter by price as well
                trade = queryset.first()
                if queryset.count() == 1:
                    self.import_source.log += f"\nOne Trade found: {trade}"
                if queryset.count() > 1:
                    self.import_source.log += f"\nMultiple similar Trades found (returning first trade): {trade}"
                return trade
        self.import_source.log += "\nNo trade was successfully matched."

    def _get_history(self, history: Dict[str, Any]) -> models.QuerySet:
        from wbportfolio.models.orders.order_proposals import OrderProposal

        if order_proposal_id := history.get("order_proposal_id"):
            # if a order proposal is provided, we delete the existing history first as otherwise, it would mess with the target weight computation
            order_proposal = OrderProposal.objects.get(id=order_proposal_id)
            order_proposal.trades.all().delete()
            order_proposal.reset_orders()
            trades = self.model.objects.none()
        else:
            trades = self.model.objects.filter(
                exclude_from_history=False,
                pending=False,
                transaction_subtype__in=[
                    self.model.Type.SUBSCRIPTION,
                    self.model.Type.REDEMPTION,
                ],  # we cannot exclude marked for deleted trade because otherwise they are never consider in the history
            )
            if transaction_date := history.get("transaction_date"):
                trades = trades.filter(transaction_date__lte=transaction_date)
            elif book_date := history.get("book_date"):
                trades = trades.filter(book_date__lte=book_date)
            if underlying_instrument_data := history.get("underlying_instrument"):
                if isinstance(underlying_instrument_data, dict):
                    trades = trades.filter(
                        **{f"underlying_instrument__{k}": v for k, v in underlying_instrument_data.items()}
                    )
                else:
                    trades = trades.filter(underlying_instrument__id=underlying_instrument_data)

            elif "underlying_instruments" in history:
                trades = trades.filter(underlying_instrument__id__in=history["underlying_instruments"])
            else:
                raise ValueError("We cannot estimate history without at least the underlying instrument")
        return trades

    def _post_processing_objects(
        self,
        created_objs: list[models.Model],
        modified_objs: list[models.Model],
        unmodified_objs: list[models.Model],
    ):
        from wbportfolio.models.orders.order_proposals import replay_as_task

        for instrument in set(
            map(lambda x: x.underlying_instrument, filter(lambda t: t.is_customer_trade, created_objs + modified_objs))
        ):
            if instrument.instrument_type.key == "product":
                update_outstanding_shares_as_task.delay(instrument.id)

        # if the trade import relates to a order proposal, we reset the TP after the import to ensure it contains the deleted positions (often forgotten by user)
        for changed_order_proposal in self.order_proposals:
            replay_as_task.delay(changed_order_proposal.id)

    def _post_processing_updated_object(self, _object):
        if _object.marked_for_deletion:
            _object.marked_for_deletion = False
            _object.save()
            self.import_source.log += "\nMarked for deletion reverted"
        if _object.underlying_instrument.instrument_type == InstrumentType.PRODUCT:
            _object.link_to_internal_trade()

    def _post_processing_created_object(self, _object):
        self._post_processing_updated_object(_object)

    def _post_processing_history(self, history: models.QuerySet):
        self.import_source.log += "===================="
        self.import_source.log += "It was a historical import and the following Trades have to be deleted:"
        for trade in history.order_by("transaction_date"):
            self.import_source.log += (
                f"{trade.transaction_date:%d.%m.%Y}: {trade.shares} {trade.bank} ==> Marked for deletion"
            )
            if trade.order_proposal:
                trade.delete()
            else:
                trade.marked_for_deletion = True
                trade.save()

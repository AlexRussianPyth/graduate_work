import datetime as dt
import time
import logging
from uuid import UUID

from services.role_updater import RoleUpdater
from services.data_enricher import DataEnricher
from services.ecom_parser import StripeEventParser
from typing import List

from models import models

logger = logging.getLogger(__name__)


class PaymentManager:
    """Управляет обработкой успешной транзакции и взаимодействует с другими сервисами"""

    def __init__(self, auth_updater: RoleUpdater, enricher: DataEnricher, model_to_process):
        self._auth_updater = auth_updater
        self._enricher = enricher
        self._model_to_process = model_to_process
        self.event_parser = StripeEventParser()

    async def watch_events(self) -> None:
        """Мониторит новые необработанные записи в БД"""
        while True:
            logger.warning("Watch New Events")
            events = await self._enricher.get_uncompleted_events(models.Event)
            if events:
                for event in events:
                    logger.warning(f"There are uncompleted event: {event.payment_system_id}")
                    if not event.data:
                        await self.mark_event_as_completed(event.payment_system_id)
                    else:
                        event_data = await self.event_parser.parse(event.data)
                        payment = await self._enricher.get_payment_info(event_data.data.payment_intent)
                        if event_data.type.name == 'payment_intent_succeeded':
                            await self._update_roles([payment.user_id], payment.subscription.roles, str(payment.end_date))
                        elif event_data.type.name == 'charge_refunded':
                            await self._update_roles(
                                [payment.user_id], payment.subscription.roles,
                                str(dt.datetime.now().date())
                            )
                        await self.mark_event_as_completed(event.payment_system_id)
                        await self.mark_payment_as_paid(payment.intent_id)
            time.sleep(5)

    async def _update_roles(self, users: List[UUID], roles: List[UUID], expired_at: str) -> None:
        """Изменяет Роли"""
        await self._auth_updater.add_roles(users=users, roles=roles, expired_at=expired_at)

    async def mark_event_as_completed(self, id: str) -> None:
        """Помечает Оплату как завершенную"""
        await self._enricher.mark_event_as_completed(models.Event, id, processed=True)
        logger.warning(f"Payment Management Completed an event {id}")

    async def mark_payment_as_paid(self, id: str) -> None:
        """Помечает Оплату как завершенную"""
        await self._enricher.mark_payment_as_completed(model=models.Payment, id=id, is_paid=True)
        logger.warning(f"Payment Management Completed on payment {id}")

    def send_notifications(self) -> None:
        """Отправляет Уведомления через сервис уведомлений"""
        raise NotImplementedError

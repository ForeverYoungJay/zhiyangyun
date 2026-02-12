from datetime import datetime
from decimal import Decimal

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.models.commerce import (
    AccountBalance,
    AccountLedger,
    InventoryLedger,
    InventoryReservation,
    ProductCategory,
    ProductSKU,
    ProductSPU,
    ShopOrder,
    ShopOrderItem,
)
from app.models.elder import Elder
from app.schemas.commerce import (
    CategoryCreate,
    InventoryChangeCreate,
    InventoryCheckCreate,
    OrderCreate,
    SkuCreate,
    SpuCreate,
)


class CommerceService:
    def _to_plain(self, obj):
        return {k: v for k, v in vars(obj).items() if not k.startswith("_")}

    def _pager(self, rows: list, page: int, page_size: int):
        total = len(rows)
        start = (page - 1) * page_size
        return {"items": rows[start:start + page_size], "total": total, "page": page, "page_size": page_size}

    def _create_ledger(self, db: Session, tenant_id: str, sku: ProductSKU, change_type: str, qty: int, before: int, after: int, remark: str = "", order_id: str | None = None):
        db.add(InventoryLedger(
            tenant_id=tenant_id,
            sku_id=sku.id,
            change_type=change_type,
            quantity=qty,
            before_stock=before,
            after_stock=after,
            remark=remark,
            related_order_id=order_id,
        ))

    def list_categories(self, db: Session, tenant_id: str):
        return db.scalars(select(ProductCategory).where(ProductCategory.tenant_id == tenant_id).order_by(ProductCategory.code.asc())).all()

    def create_category(self, db: Session, tenant_id: str, payload: CategoryCreate):
        obj = ProductCategory(tenant_id=tenant_id, **payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def list_spu(self, db: Session, tenant_id: str, page: int, page_size: int, keyword: str):
        stmt = select(ProductSPU, ProductCategory.name_zh.label("category_name")).join(ProductCategory, ProductCategory.id == ProductSPU.category_id).where(ProductSPU.tenant_id == tenant_id)
        if keyword:
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ProductSPU.name_zh.like(like), ProductSPU.subtitle_zh.like(like), ProductCategory.name_zh.like(like)))
        rows = db.execute(stmt.order_by(ProductSPU.id.desc())).all()
        return self._pager([{**self._to_plain(spu), "category_name": cname} for spu, cname in rows], page, page_size)

    def create_spu(self, db: Session, tenant_id: str, payload: SpuCreate):
        obj = ProductSPU(tenant_id=tenant_id, **payload.model_dump())
        db.add(obj)
        db.commit()
        db.refresh(obj)
        return obj

    def update_spu_status(self, db: Session, tenant_id: str, spu_id: str, status: str):
        spu = db.scalar(select(ProductSPU).where(ProductSPU.tenant_id == tenant_id, ProductSPU.id == spu_id))
        if not spu:
            raise ValueError("SPU不存在")
        spu.status = status
        db.commit()
        db.refresh(spu)
        return spu

    def list_sku(self, db: Session, tenant_id: str, page: int, page_size: int, keyword: str):
        stmt = (
            select(ProductSKU, ProductSPU.name_zh.label("spu_name"), ProductCategory.name_zh.label("category_name"))
            .join(ProductSPU, ProductSPU.id == ProductSKU.spu_id)
            .join(ProductCategory, ProductCategory.id == ProductSPU.category_id)
            .where(ProductSKU.tenant_id == tenant_id)
        )
        if keyword:
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ProductSKU.sku_name_zh.like(like), ProductSKU.sku_code.like(like), ProductSPU.name_zh.like(like)))
        rows = db.execute(stmt.order_by(ProductSKU.id.desc())).all()
        return self._pager([{**self._to_plain(sku), "spu_name": sname, "category_name": cname} for sku, sname, cname in rows], page, page_size)

    def suggest_sku(self, db: Session, tenant_id: str, keyword: str, limit: int):
        stmt = select(ProductSKU).where(ProductSKU.tenant_id == tenant_id)
        if keyword:
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ProductSKU.sku_name_zh.like(like), ProductSKU.sku_code.like(like)))
        rows = db.scalars(stmt.order_by(ProductSKU.sku_name_zh.asc()).limit(limit)).all()
        return [{"id": x.id, "name": x.sku_name_zh, "sku_code": x.sku_code, "available_stock": x.available_stock} for x in rows]

    def create_sku(self, db: Session, tenant_id: str, payload: SkuCreate):
        body = payload.model_dump()
        initial_stock = body.pop("available_stock", 0)
        obj = ProductSKU(tenant_id=tenant_id, available_stock=initial_stock, **body)
        db.add(obj)
        db.flush()
        self._create_ledger(db, tenant_id, obj, "in", initial_stock, 0, initial_stock, "SKU初始化")
        db.commit()
        db.refresh(obj)
        return obj

    def stock_in(self, db: Session, tenant_id: str, payload: InventoryChangeCreate):
        sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == payload.sku_id))
        if not sku:
            raise ValueError("SKU不存在")
        before = sku.available_stock
        sku.available_stock = before + payload.quantity
        self._create_ledger(db, tenant_id, sku, "in", payload.quantity, before, sku.available_stock, payload.remark)
        db.commit()
        return {"sku_id": sku.id, "available_stock": sku.available_stock}

    def stock_out(self, db: Session, tenant_id: str, payload: InventoryChangeCreate):
        sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == payload.sku_id))
        if not sku:
            raise ValueError("SKU不存在")
        if sku.available_stock < payload.quantity:
            raise ValueError("库存不足")
        before = sku.available_stock
        sku.available_stock = before - payload.quantity
        self._create_ledger(db, tenant_id, sku, "out", payload.quantity, before, sku.available_stock, payload.remark)
        db.commit()
        return {"sku_id": sku.id, "available_stock": sku.available_stock}

    def stock_check(self, db: Session, tenant_id: str, payload: InventoryCheckCreate):
        sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == payload.sku_id))
        if not sku:
            raise ValueError("SKU不存在")
        before = sku.available_stock
        diff = payload.actual_stock - before
        sku.available_stock = payload.actual_stock
        self._create_ledger(db, tenant_id, sku, "check", diff, before, sku.available_stock, payload.remark)
        db.commit()
        return {"sku_id": sku.id, "available_stock": sku.available_stock}

    def list_inventory_ledger(self, db: Session, tenant_id: str, page: int, page_size: int, sku_id: str):
        stmt = select(InventoryLedger, ProductSKU.sku_name_zh.label("sku_name")).join(ProductSKU, ProductSKU.id == InventoryLedger.sku_id).where(InventoryLedger.tenant_id == tenant_id)
        if sku_id:
            stmt = stmt.where(InventoryLedger.sku_id == sku_id)
        rows = db.execute(stmt.order_by(InventoryLedger.created_at.desc())).all()
        return self._pager([{**self._to_plain(log), "sku_name": sku_name} for log, sku_name in rows], page, page_size)

    def list_warnings(self, db: Session, tenant_id: str):
        rows = db.scalars(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.available_stock <= ProductSKU.warning_stock)).all()
        return [{"sku_id": x.id, "sku_name": x.sku_name_zh, "available_stock": x.available_stock, "warning_stock": x.warning_stock} for x in rows]

    def _ensure_balance(self, db: Session, tenant_id: str, elder_id: str):
        bal = db.scalar(select(AccountBalance).where(AccountBalance.tenant_id == tenant_id, AccountBalance.elder_id == elder_id))
        if bal:
            return bal
        bal = AccountBalance(tenant_id=tenant_id, elder_id=elder_id, balance=Decimal("10000.00"))
        db.add(bal)
        db.flush()
        return bal

    def _write_account_ledger(self, db: Session, tenant_id: str, elder_id: str, order_id: str, biz_type: str, amount: Decimal, direction: str, remark: str):
        bal = self._ensure_balance(db, tenant_id, elder_id)
        if direction == "debit":
            bal.balance = Decimal(str(bal.balance)) - amount
        else:
            bal.balance = Decimal(str(bal.balance)) + amount
        db.add(AccountLedger(
            tenant_id=tenant_id,
            elder_id=elder_id,
            order_id=order_id,
            biz_type=biz_type,
            amount=amount,
            direction=direction,
            balance_after=bal.balance,
            remark=remark,
        ))

    def create_order(self, db: Session, tenant_id: str, payload: OrderCreate):
        elder = db.scalar(select(Elder).where(Elder.tenant_id == tenant_id, Elder.id == payload.elder_id))
        if not elder:
            raise ValueError("长者不存在")
        order = ShopOrder(tenant_id=tenant_id, elder_id=payload.elder_id, status="created", total_amount=0, paid_amount=0)
        db.add(order)
        db.flush()

        total = Decimal("0")
        reserved_skus: list[tuple[ProductSKU, int]] = []
        for item in payload.items:
            sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == item.sku_id).with_for_update())
            if not sku:
                raise ValueError("SKU不存在")
            if sku.status != "on_shelf":
                raise ValueError(f"商品{sku.sku_name_zh}未上架")
            if sku.available_stock < item.quantity:
                raise ValueError(f"商品{sku.sku_name_zh}库存不足")
            before = sku.available_stock
            sku.available_stock -= item.quantity
            sku.reserved_stock += item.quantity
            db.add(InventoryReservation(tenant_id=tenant_id, sku_id=sku.id, order_id=order.id, quantity=item.quantity, status="reserved"))
            self._create_ledger(db, tenant_id, sku, "reserve", item.quantity, before, sku.available_stock, "下单预占", order.id)
            line_total = Decimal(str(sku.sale_price)) * item.quantity
            total += line_total
            db.add(ShopOrderItem(
                tenant_id=tenant_id,
                order_id=order.id,
                sku_id=sku.id,
                sku_name_zh=sku.sku_name_zh,
                quantity=item.quantity,
                unit_price=sku.sale_price,
                total_price=line_total,
            ))
            reserved_skus.append((sku, item.quantity))

        order.total_amount = total
        order.paid_amount = 0
        db.commit()
        db.refresh(order)
        return {**self._to_plain(order), "elder_name": elder.name}

    def _release_reservation(self, db: Session, tenant_id: str, order: ShopOrder, ledger_type: str, remark: str):
        reservations = db.scalars(select(InventoryReservation).where(InventoryReservation.tenant_id == tenant_id, InventoryReservation.order_id == order.id, InventoryReservation.status == "reserved")).all()
        for r in reservations:
            sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == r.sku_id).with_for_update())
            before = sku.available_stock
            sku.available_stock += r.quantity
            sku.reserved_stock = max(0, sku.reserved_stock - r.quantity)
            r.status = "released"
            self._create_ledger(db, tenant_id, sku, ledger_type, r.quantity, before, sku.available_stock, remark, order.id)

    def pay_order(self, db: Session, tenant_id: str, order_id: str):
        order = db.scalar(select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.id == order_id).with_for_update())
        if not order:
            raise ValueError("订单不存在")
        if order.status not in {"created"}:
            raise ValueError("当前状态不可支付")
        reservations = db.scalars(select(InventoryReservation).where(InventoryReservation.tenant_id == tenant_id, InventoryReservation.order_id == order.id, InventoryReservation.status == "reserved")).all()
        for r in reservations:
            sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == r.sku_id).with_for_update())
            before = sku.reserved_stock
            sku.reserved_stock = max(0, sku.reserved_stock - r.quantity)
            r.status = "consumed"
            self._create_ledger(db, tenant_id, sku, "out", r.quantity, before, sku.reserved_stock, "支付后出库", order.id)
        self._write_account_ledger(db, tenant_id, order.elder_id, order.id, "shop_order_pay", Decimal(str(order.total_amount)), "debit", "商城订单支付")
        order.status = "paid"
        order.paid_amount = order.total_amount
        db.commit()
        return self._to_plain(order)

    def cancel_order(self, db: Session, tenant_id: str, order_id: str, reason: str):
        order = db.scalar(select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.id == order_id).with_for_update())
        if not order:
            raise ValueError("订单不存在")
        if order.status not in {"created"}:
            raise ValueError("当前状态不可取消")
        self._release_reservation(db, tenant_id, order, "release", "取消订单释放库存")
        order.status = "cancelled"
        order.cancel_reason = reason
        db.commit()
        return self._to_plain(order)

    def refund_order(self, db: Session, tenant_id: str, order_id: str, reason: str):
        order = db.scalar(select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.id == order_id).with_for_update())
        if not order:
            raise ValueError("订单不存在")
        if order.status not in {"paid", "completed"}:
            raise ValueError("当前状态不可退款")
        items = db.scalars(select(ShopOrderItem).where(ShopOrderItem.tenant_id == tenant_id, ShopOrderItem.order_id == order.id)).all()
        for item in items:
            sku = db.scalar(select(ProductSKU).where(ProductSKU.tenant_id == tenant_id, ProductSKU.id == item.sku_id).with_for_update())
            before = sku.available_stock
            sku.available_stock += item.quantity
            self._create_ledger(db, tenant_id, sku, "refund", item.quantity, before, sku.available_stock, "订单退款回库", order.id)
        self._write_account_ledger(db, tenant_id, order.elder_id, order.id, "shop_order_refund", Decimal(str(order.paid_amount)), "credit", reason or "商城订单退款")
        order.status = "refunded"
        db.commit()
        return self._to_plain(order)

    def complete_order(self, db: Session, tenant_id: str, order_id: str):
        order = db.scalar(select(ShopOrder).where(ShopOrder.tenant_id == tenant_id, ShopOrder.id == order_id).with_for_update())
        if not order:
            raise ValueError("订单不存在")
        if order.status != "paid":
            raise ValueError("仅支付订单可完成")
        order.status = "completed"
        db.commit()
        return self._to_plain(order)

    def list_orders(self, db: Session, tenant_id: str, page: int, page_size: int, keyword: str, status: str):
        stmt = select(ShopOrder, Elder.name.label("elder_name")).join(Elder, Elder.id == ShopOrder.elder_id).where(ShopOrder.tenant_id == tenant_id)
        if keyword:
            like = f"%{keyword.strip()}%"
            stmt = stmt.where(or_(ShopOrder.id.like(like), Elder.name.like(like)))
        if status:
            stmt = stmt.where(ShopOrder.status == status)
        rows = db.execute(stmt.order_by(ShopOrder.created_at.desc())).all()
        return self._pager([{**self._to_plain(order), "elder_name": elder_name} for order, elder_name in rows], page, page_size)

    def list_account_ledger(self, db: Session, tenant_id: str, elder_id: str):
        return db.scalars(select(AccountLedger).where(AccountLedger.tenant_id == tenant_id, AccountLedger.elder_id == elder_id).order_by(AccountLedger.created_at.desc())).all()

    def list_family_orders(self, db: Session, tenant_id: str, elder_id: str):
        rows = db.execute(select(ShopOrder, Elder.name.label("elder_name")).join(Elder, Elder.id == ShopOrder.elder_id).where(ShopOrder.tenant_id == tenant_id, ShopOrder.elder_id == elder_id).order_by(ShopOrder.created_at.desc())).all()
        return [{**self._to_plain(order), "elder_name": elder_name} for order, elder_name in rows]

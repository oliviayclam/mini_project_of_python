import { dishByLevel, type Order } from "../game/types";

type Props = {
  orders: Order[];
  chill: boolean;
  onDeliver: (orderId: number) => void;
};

export function Orders({ orders, chill, onDeliver }: Props) {
  return (
    <aside className="orders" aria-label="Customer orders">
      <h2>訂單 Orders</h2>
      {orders.map((order) => {
        const pct = chill ? 100 : Math.round((order.timeLeft / order.maxTime) * 100);
        return (
          <button
            key={order.id}
            type="button"
            className="ticket"
            onClick={() => onDeliver(order.id)}
          >
            <div className="ticket-head">
              <span>單 #{order.id}</span>
              <span>{chill ? "慢慢嚟" : `${order.timeLeft}s`}</span>
            </div>
            <div className="ticket-items">
              {order.items.map((it, idx) => {
                const d = dishByLevel(it.level);
                return (
                  <div key={idx} className="ticket-item">
                    <span>
                      {d.emoji} {d.zh}
                    </span>
                    <span>
                      {it.delivered}/{it.needed}
                    </span>
                    <span className="en">{d.en}</span>
                  </div>
                );
              })}
            </div>
            <div className="ticket-bar">
              <i style={{ width: `${pct}%` }} />
            </div>
            <small>揀好點心再撳呢張單 Deliver</small>
          </button>
        );
      })}
    </aside>
  );
}

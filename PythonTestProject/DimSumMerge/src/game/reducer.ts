import {
  CELL_COUNT,
  MAX_LEVEL,
  dishByLevel,
  orderSlotCount,
  teaBoost,
  type GameState,
  type Mood,
  type Order,
  type TeaType,
} from "./types";

function emptyBoard(): (number | null)[] {
  return Array.from({ length: CELL_COUNT }, () => null);
}

function randomEmpty(board: (number | null)[]): number | null {
  const empties = board
    .map((v, i) => (v == null ? i : -1))
    .filter((i) => i >= 0);
  if (empties.length === 0) return null;
  return empties[Math.floor(Math.random() * empties.length)];
}

function spawnLevel(): number {
  return Math.random() < 0.7 ? 1 : 2;
}

export function fillStarterBoard(): (number | null)[] {
  const board = emptyBoard();
  for (let n = 0; n < 10; n += 1) {
    const i = randomEmpty(board);
    if (i == null) break;
    board[i] = spawnLevel();
  }
  return board;
}

export function orderTimeFor(mood: Mood, tea: TeaType): number {
  const base = mood === "chill" ? 999 : mood === "normal" ? 42 : 28;
  const extra = tea === "chrysanthemum" && mood !== "spicy" ? teaBoost(tea).orderTime : 1;
  return Math.round(base * extra);
}

export function makeOrder(id: number, mood: Mood, tea: TeaType): Order {
  const kindCount = Math.random() < 0.45 ? 2 : 1;
  const items = [];
  const used = new Set<number>();
  for (let k = 0; k < kindCount; k += 1) {
    let level = 3 + Math.floor(Math.random() * 3);
    while (used.has(level)) level = 3 + Math.floor(Math.random() * 3);
    used.add(level);
    items.push({
      level,
      needed: 1 + (Math.random() < 0.35 ? 1 : 0),
      delivered: 0,
    });
  }
  const maxTime = orderTimeFor(mood, tea);
  return { id, items, timeLeft: maxTime, maxTime };
}

export function createGame(mood: Mood, partySize: number, teaType: TeaType): GameState {
  const boost = teaBoost(teaType);
  const slots = orderSlotCount(partySize);
  const orders: Order[] = [];
  for (let i = 0; i < slots; i += 1) {
    orders.push(makeOrder(i + 1, mood, teaType));
  }
  return {
    mood,
    partySize,
    teaType,
    board: fillStarterBoard(),
    selected: null,
    orders,
    coins: 0,
    teaMeter: boost.teaStart,
    paused: false,
    toast: teaType === "jasmine" ? "茉莉花香～ cute tea time 🌸" : "一盅兩件，慢慢食～",
    ordersCompleted: 0,
    nextOrderId: slots + 1,
  };
}

export type GameAction =
  | { type: "SELECT"; index: number }
  | { type: "DELIVER"; orderId: number }
  | { type: "TICK" }
  | { type: "SPAWN" }
  | { type: "TOGGLE_PAUSE" }
  | { type: "CLEAR_TOAST" }
  | { type: "REWARD"; coins: number; tea: number; toast: string; extraOrder?: boolean }
  | { type: "SET_TOAST"; toast: string };

function isOrderDone(order: Order): boolean {
  return order.items.every((it) => it.delivered >= it.needed);
}

export function reducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case "TOGGLE_PAUSE":
      return { ...state, paused: !state.paused };
    case "CLEAR_TOAST":
      return { ...state, toast: null };
    case "SET_TOAST":
      return { ...state, toast: action.toast };
    case "SPAWN": {
      if (state.paused) return state;
      const board = [...state.board];
      const i = randomEmpty(board);
      if (i == null) return state;
      board[i] = spawnLevel();
      return { ...state, board };
    }
    case "TICK": {
      if (state.paused || state.mood === "chill") return state;
      const orders = state.orders
        .map((o) => ({ ...o, timeLeft: Math.max(0, o.timeLeft - 1) }))
        .filter((o) => o.timeLeft > 0);
      const lost = state.orders.length - orders.length;
      let nextId = state.nextOrderId;
      while (orders.length < orderSlotCount(state.partySize)) {
        orders.push(makeOrder(nextId, state.mood, state.teaType));
        nextId += 1;
      }
      return {
        ...state,
        orders,
        nextOrderId: nextId,
        toast: lost > 0 ? "訂單走咗… 下次快啲呀！" : state.toast,
      };
    }
    case "SELECT": {
      const { index } = action;
      const value = state.board[index];
      if (state.selected == null) {
        if (value == null) return state;
        return { ...state, selected: index };
      }
      if (state.selected === index) {
        return { ...state, selected: null };
      }
      const from = state.selected;
      const fromVal = state.board[from];
      const board = [...state.board];
      if (fromVal == null) return { ...state, selected: value == null ? null : index };

      if (value == null) {
        board[index] = fromVal;
        board[from] = null;
        return { ...state, board, selected: null };
      }
      if (value === fromVal && fromVal < MAX_LEVEL) {
        board[index] = fromVal + 1;
        board[from] = null;
        const merged = dishByLevel(fromVal + 1);
        const empty = randomEmpty(board);
        if (empty != null) board[empty] = spawnLevel();
        return {
          ...state,
          board,
          selected: null,
          toast:
            fromVal + 1 === MAX_LEVEL
              ? "一盅兩件！！Legendary！"
              : `合咗 → ${merged.emoji} ${merged.zh}`,
        };
      }
      return { ...state, selected: index };
    }
    case "DELIVER": {
      if (state.selected == null) {
        return { ...state, toast: "先揀一籠點心，再交俾客人～" };
      }
      const level = state.board[state.selected];
      if (level == null) return { ...state, selected: null };
      const order = state.orders.find((o) => o.id === action.orderId);
      if (!order) return state;
      const item = order.items.find((it) => it.level === level && it.delivered < it.needed);
      if (!item) {
        return { ...state, toast: "呢單唔要呢樣喎！" };
      }
      const board = [...state.board];
      board[state.selected] = null;
      const orders = state.orders.map((o) => {
        if (o.id !== order.id) return o;
        return {
          ...o,
          items: o.items.map((it) =>
            it === item ? { ...it, delivered: it.delivered + 1 } : it
          ),
        };
      });
      const updated = orders.find((o) => o.id === order.id)!;
      if (!isOrderDone(updated)) {
        return { ...state, board, orders, selected: null, toast: "交咗一籠！" };
      }
      const kept = orders.filter((o) => o.id !== order.id);
      let nextId = state.nextOrderId;
      kept.push(makeOrder(nextId, state.mood, state.teaType));
      nextId += 1;
      const teaGain = state.teaType === "puer" ? 18 : 12;
      return {
        ...state,
        board,
        orders: kept,
        selected: null,
        nextOrderId: nextId,
        coins: state.coins + 20 + state.partySize,
        teaMeter: Math.min(100, state.teaMeter + teaGain),
        ordersCompleted: state.ordersCompleted + 1,
        toast: state.teaType === "jasmine" ? "多謝惠顧 🌸 好可愛呀！" : "埋單前再叫多籠～ 訂單完成！",
      };
    }
    case "REWARD": {
      let orders = state.orders;
      let nextId = state.nextOrderId;
      if (action.extraOrder) {
        const first = orders[0];
        if (first) {
          orders = orders.map((o, i) =>
            i === 0
              ? {
                  ...o,
                  items: o.items.map((it, j) =>
                    j === 0 ? { ...it, needed: it.needed + 1 } : it
                  ),
                }
              : o
          );
        }
      }
      return {
        ...state,
        coins: state.coins + action.coins,
        teaMeter: Math.min(100, Math.max(0, state.teaMeter + action.tea)),
        toast: action.toast,
        orders,
        nextOrderId: nextId,
      };
    }
    default:
      return state;
  }
}

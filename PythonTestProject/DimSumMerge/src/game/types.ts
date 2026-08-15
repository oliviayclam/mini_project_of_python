export type Mood = "chill" | "normal" | "spicy";
export type TeaType =
  | "puer"
  | "jasmine"
  | "tieguanyin"
  | "chrysanthemum"
  | "xiangpian";
export type CallOut = "aaje" | "lengje" | "laumin" | "siying" | "mggoi" | "zeze";
export type MiniGameId =
  | "waitress"
  | "cart"
  | "callTea"
  | "milkTea"
  | "pineapple";
export type Screen = "mood" | "seating" | "play";
export type WaitressTactic = "sound" | "wave";

export const BOARD_SIZE = 6;
export const CELL_COUNT = BOARD_SIZE * BOARD_SIZE;
export const MAX_LEVEL = 8;

export const MOODS: { id: Mood; zh: string; en: string; hint: string }[] = [
  { id: "chill", zh: "茶 Chill", en: "Chill", hint: "No timers. NPC is sleepy. Cannot lose." },
  { id: "normal", zh: "點心 Normal", en: "Normal", hint: "Soft timers. Fair NPC." },
  { id: "spicy", zh: "辣 Spicy", en: "Spicy", hint: "Fast cart. Aggressive NPC." },
];

export const CALL_OUTS: { id: CallOut; zh: string; en: string }[] = [
  { id: "aaje", zh: "呀姐", en: "A-je" },
  { id: "lengje", zh: "靚姐", en: "Pretty je" },
  { id: "laumin", zh: "樓面", en: "Floor" },
  { id: "siying", zh: "侍應", en: "Waiter" },
  { id: "mggoi", zh: "唔該", en: "M'goi" },
  { id: "zeze", zh: "姐姐", en: "Jie jie" },
];

export const TEAS: {
  id: TeaType;
  zh: string;
  en: string;
  emoji: string;
  hint: string;
}[] = [
  { id: "puer", zh: "普洱", en: "Pu'er", emoji: "🫖", hint: "Classic. Extra tea meter." },
  { id: "jasmine", zh: "茉莉花", en: "Jasmine", emoji: "🌸", hint: "Cute extra reactions." },
  { id: "tieguanyin", zh: "鐵觀音", en: "Tieguanyin", emoji: "🍃", hint: "Tiny mini-game boost." },
  { id: "chrysanthemum", zh: "菊花", en: "Chrysanthemum", emoji: "🌼", hint: "Extra order time." },
  { id: "xiangpian", zh: "香片", en: "Xiang pian", emoji: "🍵", hint: "Balanced default." },
];

export const PARTY_SIZES = [2, 4, 5, 6, 8] as const;

export const DISHES: { level: number; emoji: string; zh: string; en: string }[] = [
  { level: 1, emoji: "🍚", zh: "米", en: "Rice" },
  { level: 2, emoji: "⚪", zh: "麵糰", en: "Dough" },
  { level: 3, emoji: "🥟", zh: "蝦餃", en: "Har gow" },
  { level: 4, emoji: "🟠", zh: "燒賣", en: "Siu mai" },
  { level: 5, emoji: "🔴", zh: "叉燒包", en: "Char siu bao" },
  { level: 6, emoji: "🍥", zh: "腸粉", en: "Cheung fun" },
  { level: 7, emoji: "🥧", zh: "蛋撻", en: "Egg tart" },
  { level: 8, emoji: "🏆", zh: "一盅兩件", en: "Yum cha set" },
];

export const MINI_GAMES: { id: MiniGameId; zh: string; en: string }[] = [
  { id: "waitress", zh: "叫人", en: "Waitress" },
  { id: "cart", zh: "點心車", en: "Dim sum cart" },
  { id: "callTea", zh: "揭蓋叫茶", en: "Call tea" },
  { id: "milkTea", zh: "拉茶", en: "Milk-tea pull" },
  { id: "pineapple", zh: "菠蘿油", en: "Pineapple bun" },
];

export interface OrderItem {
  level: number;
  needed: number;
  delivered: number;
}

export interface Order {
  id: number;
  items: OrderItem[];
  timeLeft: number;
  maxTime: number;
}

export interface GameState {
  mood: Mood;
  partySize: number;
  teaType: TeaType;
  board: (number | null)[];
  selected: number | null;
  orders: Order[];
  coins: number;
  teaMeter: number;
  paused: boolean;
  toast: string | null;
  ordersCompleted: number;
  nextOrderId: number;
}

export function dishByLevel(level: number) {
  return DISHES.find((d) => d.level === level) ?? DISHES[0];
}

export function orderSlotCount(partySize: number): number {
  if (partySize <= 2) return 1;
  if (partySize <= 4) return 2;
  if (partySize <= 6) return 3;
  return 4;
}

export function npcSkill(mood: Mood): number {
  if (mood === "chill") return 0.22;
  if (mood === "normal") return 0.48;
  return 0.72;
}

export function teaBoost(tea: TeaType): { teaStart: number; orderTime: number; miniEase: number } {
  if (tea === "puer") return { teaStart: 28, orderTime: 1, miniEase: 1 };
  if (tea === "jasmine") return { teaStart: 12, orderTime: 1, miniEase: 1 };
  if (tea === "tieguanyin") return { teaStart: 12, orderTime: 1, miniEase: 1.18 };
  if (tea === "chrysanthemum") return { teaStart: 12, orderTime: 1.3, miniEase: 1 };
  return { teaStart: 12, orderTime: 1, miniEase: 1 };
}

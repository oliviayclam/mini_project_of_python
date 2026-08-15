import { MINI_GAMES, MOODS, type MiniGameId, type Mood } from "../game/types";

type Props = {
  mood: Mood;
  onMood: (m: Mood) => void;
  onPick: (id: MiniGameId) => void;
  onClose: () => void;
};

export function BattlePicker({ mood, onMood, onPick, onClose }: Props) {
  return (
    <div className="overlay">
      <div className="panel">
        <h2>對決 Battle vs NPC</h2>
        <p className="muted">揀難度同小遊戲 Pick level + mini-game</p>
        <div className="row">
          {MOODS.map((m) => (
            <button
              key={m.id}
              type="button"
              className={`chip ${mood === m.id ? "on" : ""}`}
              onClick={() => onMood(m.id)}
            >
              {m.zh}
            </button>
          ))}
        </div>
        <div className="choice-grid">
          {MINI_GAMES.map((g) => (
            <button key={g.id} type="button" className="choice" onClick={() => onPick(g.id)}>
              <b>{g.zh}</b>
              <span>{g.en}</span>
            </button>
          ))}
        </div>
        <button type="button" className="ghost" onClick={onClose}>
          返去食茶 Back
        </button>
      </div>
    </div>
  );
}

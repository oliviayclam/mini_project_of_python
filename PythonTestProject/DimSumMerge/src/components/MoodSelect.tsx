import { MOODS, type Mood } from "../game/types";

type Props = {
  onPick: (mood: Mood) => void;
};

export function MoodSelect({ onPick }: Props) {
  return (
    <section className="scene mood-select">
      <div className="lanterns" aria-hidden>
        <span>🏮</span>
        <span>🏮</span>
        <span>🏮</span>
      </div>
      <p className="eyebrow">香港點心 · cute yum cha</p>
      <h1>點心合合樂</h1>
      <p className="subtitle">Yum Cha Merge</p>
      <p className="lead">
        合兩籠相同點心 → 下一級。完成訂單，同 NPC 鬥叫人、搶點心車。
        <br />
        Merge two same dishes. Complete orders. Battle NPCs.
      </p>
      <div className="choice-grid">
        {MOODS.map((m) => (
          <button key={m.id} type="button" className={`choice mood-${m.id}`} onClick={() => onPick(m.id)}>
            <b>{m.zh}</b>
            <span>{m.en}</span>
            <small>{m.hint}</small>
          </button>
        ))}
      </div>
    </section>
  );
}

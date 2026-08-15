import { TEAS, type GameState } from "../game/types";

type Props = {
  state: GameState;
  muted: boolean;
  volume: number;
  onPause: () => void;
  onMute: () => void;
  onVolume: (v: number) => void;
  onBattle: () => void;
};

export function Hud({ state, muted, volume, onPause, onMute, onVolume, onBattle }: Props) {
  const tea = TEAS.find((t) => t.id === state.teaType)!;
  return (
    <header className="hud">
      <div className="hud-brand">
        <strong>點心合合樂</strong>
        <span>Yum Cha Merge</span>
      </div>
      <div className="hud-stats">
        <span>🪙 {state.coins}</span>
        <span>
          {tea.emoji} {tea.zh} · {state.partySize}位
        </span>
        <span className="tea-meter">
          茶
          <i>
            <b style={{ width: `${state.teaMeter}%` }} />
          </i>
        </span>
        <span>單 {state.ordersCompleted}</span>
      </div>
      <div className="hud-actions">
        <button type="button" onClick={onBattle}>
          對決 Battle
        </button>
        <button type="button" onClick={onPause}>
          {state.paused ? "繼續" : "暫停"} Pause
        </button>
        <button type="button" onClick={onMute}>
          {muted ? "🔇" : "🔊"}
        </button>
        <input
          type="range"
          min={0}
          max={1}
          step={0.05}
          value={volume}
          aria-label="Volume"
          onChange={(e) => onVolume(Number(e.target.value))}
        />
      </div>
    </header>
  );
}

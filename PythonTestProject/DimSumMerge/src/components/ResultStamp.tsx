type Props = {
  win: boolean;
  chill: boolean;
  game: string;
  npcLine: string;
  onClose: () => void;
};

export function ResultStamp({ win, chill, npcLine, onClose }: Props) {
  const ok = win || chill;
  const title = ok ? (win ? "WIN 贏咗！" : "都算贏 Chill 🍵") : "慘敗 LOSE";
  return (
    <div className="result">
      <div className={`stamp ${ok ? "win" : "lose"}`}>{title}</div>
      <p className="npc-line">{npcLine}</p>
      <button type="button" className="choice" onClick={onClose}>
        返枱 Back to table
      </button>
    </div>
  );
}

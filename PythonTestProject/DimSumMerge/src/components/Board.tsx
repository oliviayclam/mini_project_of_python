import { dishByLevel, type GameState } from "../game/types";

type Props = {
  board: GameState["board"];
  selected: number | null;
  onSelect: (index: number) => void;
};

export function Board({ board, selected, onSelect }: Props) {
  return (
    <div className="board" role="grid" aria-label="Dim sum merge board">
      {board.map((level, i) => {
        const dish = level == null ? null : dishByLevel(level);
        return (
          <button
            key={i}
            type="button"
            className={`tile ${selected === i ? "selected" : ""} ${level == null ? "empty" : `lv-${level}`}`}
            onClick={() => onSelect(i)}
          >
            {dish ? (
              <>
                <span className="tile-emoji">{dish.emoji}</span>
                <span className="tile-zh">{dish.zh}</span>
                <span className="tile-en">{dish.en}</span>
              </>
            ) : (
              <span className="tile-empty">籠</span>
            )}
          </button>
        );
      })}
    </div>
  );
}

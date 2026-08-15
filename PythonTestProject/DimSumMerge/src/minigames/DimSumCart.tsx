import { useEffect, useMemo, useRef, useState } from "react";
import { ResultStamp } from "../components/ResultStamp";
import { useAudio } from "../audio/AudioProvider";
import { DISHES, npcSkill, teaBoost, type Mood, type TeaType } from "../game/types";

type Props = {
  mood: Mood;
  tea: TeaType;
  targetLevel: number;
  onFinish: (win: boolean) => void;
};

export function DimSumCart({ mood, tea, targetLevel, onFinish }: Props) {
  const audio = useAudio();
  const [done, setDone] = useState<"win" | "lose" | null>(null);
  const [x, setX] = useState(-10);
  const locked = useRef(false);
  const skill = npcSkill(mood);
  const ease = teaBoost(tea).miniEase;
  const speed = (mood === "spicy" ? 1.6 : mood === "normal" ? 1.1 : 0.7) / ease;
  const npcMs = mood === "chill" ? 8000 : Math.round((2200 - skill * 900) * ease);

  const carts = useMemo(() => {
    const pool = [3, 4, 5, 6, 7].filter((l) => l !== targetLevel);
    const others = pool.sort(() => Math.random() - 0.5).slice(0, 3);
    const items = [...others, targetLevel].sort(() => Math.random() - 0.5);
    return items.map((level, i) => ({ id: i, level, dish: DISHES[level - 1] }));
  }, [targetLevel]);

  useEffect(() => {
    audio.playBgm("cart");
    audio.playSfx("bell");
  }, [audio]);

  useEffect(() => {
    let raf = 0;
    let last = performance.now();
    const loop = (now: number) => {
      const dt = (now - last) / 16.6;
      last = now;
      setX((v) => v + speed * dt);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const npc = window.setTimeout(() => {
      if (!locked.current) {
        locked.current = true;
        audio.playSfx("lose");
        setDone("lose");
      }
    }, npcMs);
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(npc);
    };
  }, [audio, npcMs, speed]);

  const pick = (level: number) => {
    if (locked.current) return;
    locked.current = true;
    const win = level === targetLevel;
    audio.playSfx(win ? "win" : "lose");
    setDone(win ? "win" : "lose");
  };

  if (done) {
    const win = done === "win";
    return (
      <ResultStamp
        win={win}
        chill={mood === "chill"}
        game="cart"
        npcLine={win ? "NPC：「呀得，呢籠我哋要唔到。」" : "NPC：「呢籠我哋先！」"}
        onClose={() => onFinish(win || mood === "chill")}
      />
    );
  }

  const want = DISHES[targetLevel - 1];
  return (
    <div className="minigame">
      <h2>點心車 Dim Sum Cart</h2>
      <p className="bubble">
        <strong>要呢籠：{want.emoji} {want.zh}</strong>
        <span>Grab {want.en} first</span>
      </p>
      <div className="cart-lane">
        <div className="cart" style={{ transform: `translateX(${x}%)` }}>
          <span className="cart-emoji">🛒</span>
          {carts.map((c) => (
            <button key={c.id} type="button" className="steamer" onClick={() => pick(c.level)}>
              <span>{c.dish.emoji}</span>
              <small>{c.dish.zh}</small>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}

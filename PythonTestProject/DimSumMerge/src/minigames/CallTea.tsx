import { useEffect, useRef, useState } from "react";
import { ResultStamp } from "../components/ResultStamp";
import { useAudio } from "../audio/AudioProvider";
import { TEAS, npcSkill, teaBoost, type Mood, type TeaType } from "../game/types";

type Props = {
  mood: Mood;
  tea: TeaType;
  onFinish: (win: boolean) => void;
};

export function CallTea({ mood, tea, onFinish }: Props) {
  const audio = useAudio();
  const [look, setLook] = useState(0);
  const [done, setDone] = useState<"win" | "lose" | null>(null);
  const looking = useRef(false);
  const locked = useRef(false);
  const teaInfo = TEAS.find((t) => t.id === tea)!;
  const skill = npcSkill(mood);
  const ease = teaBoost(tea).miniEase;

  useEffect(() => {
    audio.playBgm("callTea");
  }, [audio]);

  useEffect(() => {
    let raf = 0;
    const start = performance.now();
    const loop = (now: number) => {
      const p = (Math.sin((now - start) / (420 / ease)) + 1) * 50;
      setLook(p);
      looking.current = p > (mood === "spicy" ? 72 : 64);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const npc = window.setTimeout(
      () => {
        if (!locked.current && Math.random() < skill + 0.15) {
          locked.current = true;
          audio.playSfx("lose");
          setDone("lose");
        }
      },
      mood === "chill" ? 9000 : 4200
    );
    return () => {
      cancelAnimationFrame(raf);
      clearTimeout(npc);
    };
  }, [audio, ease, mood, skill]);

  const flip = () => {
    if (locked.current) return;
    locked.current = true;
    const win = looking.current;
    audio.playSfx(win ? "clink" : "lose");
    if (win) audio.playSfx("win");
    setDone(win ? "win" : "lose");
  };

  if (done) {
    const win = done === "win";
    return (
      <ResultStamp
        win={win}
        chill={mood === "chill"}
        game="callTea"
        npcLine={
          win
            ? `續咗 ${teaInfo.zh}！NPC：「下局我哋先。」`
            : "NPC 揭蓋快過你，茶去咗隔壁枱。"
        }
        onClose={() => onFinish(win || mood === "chill")}
      />
    );
  }

  return (
    <div className="minigame">
      <h2>揭蓋叫茶 Call tea</h2>
      <p className="bubble">
        <strong>續 {teaInfo.emoji} {teaInfo.zh}</strong>
        <span>Flip the lid when she is looking</span>
      </p>
      <div className="tea-stage">
        <div className={`auntie ${look > (mood === "spicy" ? 72 : 64) ? "looking" : ""}`}>
          🫖👀
          <small>{look > (mood === "spicy" ? 72 : 64) ? "睇住你" : "行開咗"}</small>
        </div>
        <div className="look-bar">
          <i style={{ width: `${look}%` }} />
        </div>
        <button type="button" className="shout" onClick={flip}>
          揭蓋 Flip lid
        </button>
      </div>
    </div>
  );
}

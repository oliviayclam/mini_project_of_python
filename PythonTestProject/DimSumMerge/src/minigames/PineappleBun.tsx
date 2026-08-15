import { useEffect, useRef, useState } from "react";
import { ResultStamp } from "../components/ResultStamp";
import { useAudio } from "../audio/AudioProvider";
import { npcSkill, teaBoost, type Mood, type TeaType } from "../game/types";

const STEPS = [
  { zh: "切開菠蘿包", en: "Split the bun", emoji: "🍍" },
  { zh: "塞牛油", en: "Slap in butter", emoji: "🧈" },
  { zh: "斟奶茶", en: "Pour milk tea", emoji: "🥛" },
];

type Props = {
  mood: Mood;
  tea: TeaType;
  onFinish: (win: boolean) => void;
};

export function PineappleBun({ mood, tea, onFinish }: Props) {
  const audio = useAudio();
  const [step, setStep] = useState(0);
  const [needle, setNeedle] = useState(0);
  const [npcStep, setNpcStep] = useState(0);
  const [done, setDone] = useState<"win" | "lose" | null>(null);
  const val = useRef(0);
  const dir = useRef(1);
  const finished = useRef(false);
  const skill = npcSkill(mood);
  const ease = teaBoost(tea).miniEase;
  const speed = (mood === "spicy" ? 2.2 : mood === "normal" ? 1.5 : 0.9) / ease;

  useEffect(() => {
    audio.playBgm("pineapple");
  }, [audio]);

  useEffect(() => {
    let raf = 0;
    const loop = () => {
      val.current += dir.current * speed;
      if (val.current >= 100) dir.current = -1;
      if (val.current <= 0) dir.current = 1;
      setNeedle(val.current);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const npc = window.setInterval(() => {
      if (finished.current) return;
      if (Math.random() < skill) {
        setNpcStep((s) => {
          const n = s + 1;
          if (n >= 3 && !finished.current) {
            finished.current = true;
            audio.playSfx("lose");
            setDone("lose");
          }
          return n;
        });
      }
    }, 1400);
    return () => {
      cancelAnimationFrame(raf);
      clearInterval(npc);
    };
  }, [audio, skill, speed]);

  const tap = () => {
    if (done || finished.current) return;
    const hit = needle > 42 && needle < 72;
    if (!hit) {
      finished.current = true;
      audio.playSfx("lose");
      setDone("lose");
      return;
    }
    audio.playSfx("pop");
    if (step >= 2) {
      finished.current = true;
      audio.playSfx("win");
      setDone("win");
    } else {
      setStep(step + 1);
    }
  };

  if (done) {
    const win = done === "win";
    return (
      <ResultStamp
        win={win}
        chill={mood === "chill"}
        game="pineapple"
        npcLine={win ? "菠蘿油 + 奶茶 combo！" : "牛油溶咗… NPC 食咗你嗰件。"}
        onClose={() => onFinish(win || mood === "chill")}
      />
    );
  }

  const cur = STEPS[step];
  return (
    <div className="minigame">
      <h2>菠蘿油 Pineapple bun</h2>
      <p className="bubble">
        <strong>
          {cur.emoji} {cur.zh} ({step + 1}/3)
        </strong>
        <span>
          {cur.en} · NPC {Math.min(npcStep, 3)}/3
        </span>
      </p>
      <div className="meter">
        <div className="green" />
        <div className="needle" style={{ left: `${needle}%` }} />
      </div>
      <button type="button" className="shout" onClick={tap}>
        {cur.zh}！
      </button>
    </div>
  );
}

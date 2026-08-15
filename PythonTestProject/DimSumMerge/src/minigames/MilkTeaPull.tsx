import { useEffect, useRef, useState } from "react";
import { ResultStamp } from "../components/ResultStamp";
import { useAudio } from "../audio/AudioProvider";
import { npcSkill, teaBoost, type Mood, type TeaType } from "../game/types";

type Props = {
  mood: Mood;
  tea: TeaType;
  onFinish: (win: boolean) => void;
};

export function MilkTeaPull({ mood, tea, onFinish }: Props) {
  const audio = useAudio();
  const [beat, setBeat] = useState(0);
  const [fill, setFill] = useState(8);
  const [npcFill, setNpcFill] = useState(6);
  const [spill, setSpill] = useState(0);
  const [done, setDone] = useState<"win" | "lose" | null>(null);
  const inZone = useRef(false);
  const fillRef = useRef(8);
  const npcRef = useRef(6);
  const spillRef = useRef(0);
  const finished = useRef(false);
  const skill = npcSkill(mood);
  const ease = teaBoost(tea).miniEase;
  const period = (mood === "spicy" ? 520 : mood === "normal" ? 720 : 980) / ease;

  useEffect(() => {
    audio.playBgm("milkTea");
  }, [audio]);

  useEffect(() => {
    const start = performance.now();
    let raf = 0;
    const loop = (now: number) => {
      const p = ((now - start) / period) % 1;
      const pos = p < 0.5 ? p * 200 : (1 - p) * 200;
      setBeat(pos);
      inZone.current = pos > 40 && pos < 70;
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const npc = window.setInterval(() => {
      if (finished.current) return;
      npcRef.current = Math.min(100, npcRef.current + skill * 8);
      setNpcFill(npcRef.current);
      if (npcRef.current >= 100 && fillRef.current < 100) {
        finished.current = true;
        audio.playSfx("lose");
        setDone("lose");
      }
    }, 400);
    const end = window.setTimeout(() => {
      if (finished.current) return;
      finished.current = true;
      const win = fillRef.current >= npcRef.current && spillRef.current < 3;
      audio.playSfx(win ? "win" : "lose");
      setDone(win ? "win" : "lose");
    }, 10000);
    return () => {
      cancelAnimationFrame(raf);
      clearInterval(npc);
      clearTimeout(end);
    };
  }, [audio, period, skill]);

  const pull = () => {
    if (done || finished.current) return;
    if (inZone.current) {
      fillRef.current = Math.min(100, fillRef.current + 12);
      setFill(fillRef.current);
      audio.playSfx("pop");
      if (fillRef.current >= 100) {
        finished.current = true;
        audio.playSfx("win");
        setDone("win");
      }
    } else {
      spillRef.current += 1;
      setSpill(spillRef.current);
      fillRef.current = Math.max(0, fillRef.current - 8);
      setFill(fillRef.current);
      if (spillRef.current >= 3) {
        finished.current = true;
        audio.playSfx("lose");
        setDone("lose");
      }
    }
  };

  if (done) {
    const win = done === "win";
    return (
      <ResultStamp
        win={win}
        chill={mood === "chill"}
        game="milkTea"
        npcLine={win ? "絲襪奶茶拉到起絲！" : "瀉咗啦… NPC 笑你。"}
        onClose={() => onFinish(win || mood === "chill")}
      />
    );
  }

  return (
    <div className="minigame">
      <h2>拉茶 Milk-tea pull</h2>
      <p className="muted">
        You {Math.round(fill)}% · NPC {Math.round(npcFill)}% · spills {spill}/3
      </p>
      <div className="pull-stage">
        <div className="tin">🥫</div>
        <div className="stream" style={{ height: `${beat}%` }} />
        <div className="tin">🥫</div>
      </div>
      <div className="meter">
        <div className="green" />
        <div className="needle" style={{ left: `${beat}%` }} />
      </div>
      <button type="button" className="shout" onClick={pull}>
        拉！ Pull
      </button>
    </div>
  );
}

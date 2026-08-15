import { useEffect, useRef, useState } from "react";
import { ResultStamp } from "../components/ResultStamp";
import { useAudio } from "../audio/AudioProvider";
import {
  CALL_OUTS,
  npcSkill,
  teaBoost,
  type CallOut,
  type Mood,
  type TeaType,
  type WaitressTactic,
} from "../game/types";

type Props = {
  mood: Mood;
  tea: TeaType;
  onFinish: (win: boolean) => void;
};

export function WaitressBattle({ mood, tea, onFinish }: Props) {
  const audio = useAudio();
  const [call, setCall] = useState<CallOut | null>(null);
  const [tactic, setTactic] = useState<WaitressTactic | null>(null);
  const [done, setDone] = useState<"win" | "lose" | null>(null);
  const npcCall = CALL_OUTS[(Date.now() >> 3) % CALL_OUTS.length];
  const ease = teaBoost(tea).miniEase;
  const skill = npcSkill(mood);

  useEffect(() => {
    audio.playBgm("waitress");
  }, [audio]);

  const finish = (win: boolean) => {
    audio.playSfx(win ? "win" : "lose");
    setDone(win ? "win" : "lose");
  };

  if (done) {
    const win = done === "win";
    return (
      <ResultStamp
        win={win}
        chill={mood === "chill"}
        game="waitress"
        npcLine={win ? `NPC 喊「${npcCall.zh}」都遲咗！` : `NPC 搶先喊「${npcCall.zh}」！`}
        onClose={() => onFinish(win || mood === "chill")}
      />
    );
  }

  if (!call) {
    return (
      <div className="minigame">
        <h2>叫人 Waitress</h2>
        <p className="bubble">
          <strong>點叫我呀？</strong>
          <span>How do you call her?</span>
        </p>
        <div className="choice-grid">
          {CALL_OUTS.map((c) => (
            <button key={c.id} type="button" className="choice" onClick={() => setCall(c.id)}>
              <b>{c.zh}</b>
              <span>{c.en}</span>
            </button>
          ))}
        </div>
      </div>
    );
  }

  if (!tactic) {
    const label = CALL_OUTS.find((c) => c.id === call)!.zh;
    return (
      <div className="minigame">
        <h2>你會喊「{label}」</h2>
        <div className="choice-grid">
          <button type="button" className="choice" onClick={() => setTactic("sound")}>
            <b>叫人 Sound</b>
            <span>Tap 「{label}」 on the beat</span>
          </button>
          <button type="button" className="choice" onClick={() => setTactic("wave")}>
            <b>揮手 Wave</b>
            <span>Release in the green zone</span>
          </button>
        </div>
      </div>
    );
  }

  if (tactic === "sound") {
    return (
      <SoundRound
        callZh={CALL_OUTS.find((c) => c.id === call)!.zh}
        mood={mood}
        skill={skill}
        ease={ease}
        onDone={finish}
      />
    );
  }
  return <WaveRound mood={mood} skill={skill} ease={ease} onDone={finish} />;
}

function SoundRound({
  callZh,
  mood,
  skill,
  ease,
  onDone,
}: {
  callZh: string;
  mood: Mood;
  skill: number;
  ease: number;
  onDone: (win: boolean) => void;
}) {
  const [pos, setPos] = useState(0);
  const [hits, setHits] = useState(0);
  const [npc, setNpc] = useState(0);
  const hitsRef = useRef(0);
  const npcRef = useRef(0);
  const inBeat = useRef(false);

  useEffect(() => {
    const start = performance.now();
    let raf = 0;
    const period = 1400 / ease;
    const loop = (now: number) => {
      const t = (now - start) / period;
      const p = (t % 1) * 100;
      setPos(p);
      inBeat.current = Math.abs(p - 72) < (mood === "spicy" ? 8 : 12);
      raf = requestAnimationFrame(loop);
    };
    raf = requestAnimationFrame(loop);
    const npcTimer = window.setInterval(() => {
      if (Math.random() < skill) {
        npcRef.current += 1;
        setNpc(npcRef.current);
      }
    }, 900);
    const end = window.setTimeout(() => {
      onDone(hitsRef.current > npcRef.current);
    }, 9000);
    return () => {
      cancelAnimationFrame(raf);
      clearInterval(npcTimer);
      clearTimeout(end);
    };
  }, [ease, mood, onDone, skill]);

  return (
    <div className="minigame">
      <h2>等佢行過再喊「{callZh}」</h2>
      <p className="muted">
        You {hits} · NPC {npc}
      </p>
      <div className="walk-track">
        <div className="hot-zone" />
        <div className="waitress-walk" style={{ left: `${Math.min(pos, 92)}%` }}>
          💁‍♀️
        </div>
      </div>
      <button
        type="button"
        className="shout"
        onClick={() => {
          if (inBeat.current) {
            hitsRef.current += 1;
            setHits(hitsRef.current);
          }
        }}
      >
        {callZh}！
      </button>
    </div>
  );
}

function WaveRound({
  mood,
  skill,
  ease,
  onDone,
}: {
  mood: Mood;
  skill: number;
  ease: number;
  onDone: (win: boolean) => void;
}) {
  const [needle, setNeedle] = useState(8);
  const holding = useRef(false);
  const value = useRef(8);
  const ended = useRef(false);

  useEffect(() => {
    let raf = 0;
    const tick = () => {
      if (holding.current) {
        value.current = Math.min(100, value.current + 1.4 * ease);
      } else {
        value.current = Math.max(0, value.current - 0.6);
      }
      setNeedle(value.current);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [ease]);

  const release = () => {
    if (ended.current) return;
    holding.current = false;
    ended.current = true;
    const green = mood === "spicy" ? [62, 78] : [55, 82];
    const hit = value.current >= green[0] && value.current <= green[1];
    const npcHit = Math.random() < skill;
    onDone(hit && (mood === "chill" || !npcHit || value.current > 68));
  };

  return (
    <div className="minigame">
      <h2>揮手 Wave</h2>
      <p className="muted">Hold, then release in the green</p>
      <div className="meter">
        <div className="green" />
        <div className="needle" style={{ left: `${needle}%` }} />
      </div>
      <button
        type="button"
        className="shout"
        onMouseDown={() => {
          holding.current = true;
        }}
        onMouseUp={release}
        onMouseLeave={() => {
          if (holding.current) release();
        }}
        onTouchStart={(e) => {
          e.preventDefault();
          holding.current = true;
        }}
        onTouchEnd={(e) => {
          e.preventDefault();
          release();
        }}
      >
        揮手～ Hold
      </button>
    </div>
  );
}

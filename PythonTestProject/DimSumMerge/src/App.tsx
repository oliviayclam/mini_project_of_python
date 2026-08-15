import { useEffect, useReducer, useRef, useState } from "react";
import { useAudio } from "./audio/AudioProvider";
import { BattlePicker } from "./components/BattlePicker";
import { Board } from "./components/Board";
import { Hud } from "./components/Hud";
import { MoodSelect } from "./components/MoodSelect";
import { Orders } from "./components/Orders";
import { Seating } from "./components/Seating";
import { createGame, reducer } from "./game/reducer";
import { type MiniGameId, type Mood, type Screen, type TeaType } from "./game/types";
import { CallTea } from "./minigames/CallTea";
import { DimSumCart } from "./minigames/DimSumCart";
import { MilkTeaPull } from "./minigames/MilkTeaPull";
import { PineappleBun } from "./minigames/PineappleBun";
import { WaitressBattle } from "./minigames/WaitressBattle";

const MINIS: MiniGameId[] = ["waitress", "cart", "callTea", "milkTea", "pineapple"];

export default function App() {
  const audio = useAudio();
  const [screen, setScreen] = useState<Screen>("mood");
  const [mood, setMood] = useState<Mood>("normal");
  const [seed, setSeed] = useState<{ party: number; tea: TeaType } | null>(null);

  return (
    <div className="app">
      {screen === "mood" && (
        <MoodSelect
          onPick={(m) => {
            audio.unlock();
            setMood(m);
            setScreen("seating");
          }}
        />
      )}
      {screen === "seating" && (
        <Seating
          onDone={(party, tea) => {
            audio.unlock();
            setSeed({ party, tea });
            setScreen("play");
          }}
        />
      )}
      {screen === "play" && seed && (
        <Play
          key={`${mood}-${seed.party}-${seed.tea}`}
          mood={mood}
          partySize={seed.party}
          tea={seed.tea}
          onHome={() => {
            setSeed(null);
            setScreen("mood");
          }}
        />
      )}
    </div>
  );
}

function Play({
  mood,
  partySize,
  tea,
  onHome,
}: {
  mood: Mood;
  partySize: number;
  tea: TeaType;
  onHome: () => void;
}) {
  const audio = useAudio();
  const [state, dispatch] = useReducer(reducer, null, () =>
    createGame(mood, partySize, tea)
  );
  const [battleMood, setBattleMood] = useState<Mood>(mood);
  const [picker, setPicker] = useState(false);
  const [mini, setMini] = useState<MiniGameId | null>(null);
  const lastEvent = useRef(0);

  useEffect(() => {
    if (!mini) audio.playBgm("table");
  }, [audio, mini]);

  useEffect(() => {
    if (state.paused || mini) return undefined;
    const tick = window.setInterval(() => dispatch({ type: "TICK" }), 1000);
    const spawn = window.setInterval(() => dispatch({ type: "SPAWN" }), 5200);
    return () => {
      clearInterval(tick);
      clearInterval(spawn);
    };
  }, [mini, state.paused]);

  useEffect(() => {
    if (!state.toast) return undefined;
    const t = window.setTimeout(() => dispatch({ type: "CLEAR_TOAST" }), 2400);
    return () => clearTimeout(t);
  }, [state.toast]);

  useEffect(() => {
    if (state.paused) audio.pauseBgm();
    else if (!mini) audio.resumeBgm();
  }, [audio, mini, state.paused]);

  useEffect(() => {
    if (mini || state.paused) return;
    if (
      state.ordersCompleted > 0 &&
      state.ordersCompleted % 2 === 0 &&
      state.ordersCompleted !== lastEvent.current
    ) {
      lastEvent.current = state.ordersCompleted;
      if (Math.random() < 0.45) {
        setMini(MINIS[Math.floor(Math.random() * MINIS.length)]);
      }
    }
  }, [mini, state.ordersCompleted, state.paused]);

  const wantLevel = state.orders[0]?.items[0]?.level ?? 4;

  const finishMini = (id: MiniGameId, win: boolean) => {
    audio.playBgm("table");
    setMini(null);
    dispatch({
      type: "REWARD",
      coins: win ? 30 : 4,
      tea: win ? 16 : 2,
      extraOrder: win && id === "waitress",
      toast: win ? "靚姐記住你啦！" : "下次再叫大聲啲～",
    });
  };

  const select = (index: number) => {
    const from = state.selected;
    const fromVal = from != null ? state.board[from] : null;
    const toVal = state.board[index];
    dispatch({ type: "SELECT", index });
    if (from != null && fromVal != null && fromVal === toVal && from !== index) {
      audio.playSfx("merge");
    } else {
      audio.playSfx("pop");
    }
  };

  return (
    <div className="play">
      <Hud
        state={state}
        muted={audio.muted}
        volume={audio.volume}
        onPause={() => dispatch({ type: "TOGGLE_PAUSE" })}
        onMute={() => audio.setMuted(!audio.muted)}
        onVolume={(v) => audio.setVolume(v)}
        onBattle={() => setPicker(true)}
      />
      {state.toast && <div className="toast">{state.toast}</div>}
      <div className="table">
        <Board board={state.board} selected={state.selected} onSelect={select} />
        <Orders
          orders={state.orders}
          chill={state.mood === "chill"}
          onDeliver={(id) => {
            audio.playSfx("clink");
            dispatch({ type: "DELIVER", orderId: id });
          }}
        />
      </div>
      <footer className="help">
        <span>撳兩籠相同 → 合成。撳訂單交點心。 Tap two same steamers, then the ticket.</span>
        <button type="button" className="ghost" onClick={onHome}>
          唔該埋單 Leave
        </button>
      </footer>
      {state.paused && !mini && (
        <div className="overlay">
          <div className="panel">
            <h2>暫停 Pause</h2>
            <p>Streamers can talk here ✨</p>
            <button type="button" className="choice" onClick={() => dispatch({ type: "TOGGLE_PAUSE" })}>
              繼續 Continue
            </button>
          </div>
        </div>
      )}
      {picker && (
        <BattlePicker
          mood={battleMood}
          onMood={setBattleMood}
          onPick={(id) => {
            setPicker(false);
            setMini(id);
          }}
          onClose={() => setPicker(false)}
        />
      )}
      {mini && (
        <div className="overlay mini-overlay">
          {mini === "waitress" && (
            <WaitressBattle mood={battleMood} tea={tea} onFinish={(w) => finishMini("waitress", w)} />
          )}
          {mini === "cart" && (
            <DimSumCart
              mood={battleMood}
              tea={tea}
              targetLevel={wantLevel}
              onFinish={(w) => finishMini("cart", w)}
            />
          )}
          {mini === "callTea" && (
            <CallTea mood={battleMood} tea={tea} onFinish={(w) => finishMini("callTea", w)} />
          )}
          {mini === "milkTea" && (
            <MilkTeaPull mood={battleMood} tea={tea} onFinish={(w) => finishMini("milkTea", w)} />
          )}
          {mini === "pineapple" && (
            <PineappleBun mood={battleMood} tea={tea} onFinish={(w) => finishMini("pineapple", w)} />
          )}
        </div>
      )}
    </div>
  );
}

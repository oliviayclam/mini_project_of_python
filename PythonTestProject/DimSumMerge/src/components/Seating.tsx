import { useEffect, useState } from "react";
import { useAudio } from "../audio/AudioProvider";
import { PARTY_SIZES, TEAS, type TeaType } from "../game/types";

const NPC_LINES = [
  { n: 4, tea: "普洱", call: "呀姐，四位！" },
  { n: 6, tea: "菊花", call: "樓面，六位呀！" },
  { n: 2, tea: "茉莉花", call: "靚姐，兩位～" },
  { n: 8, tea: "香片", call: "唔該，八位！" },
];

type Props = {
  onDone: (partySize: number, tea: TeaType) => void;
};

export function Seating({ onDone }: Props) {
  const audio = useAudio();
  const [step, setStep] = useState<"people" | "tea">("people");
  const [partySize, setPartySize] = useState<number | null>(null);
  const npc = NPC_LINES[Math.floor(Date.now() / 8000) % NPC_LINES.length];

  useEffect(() => {
    audio.playBgm("seating");
  }, [audio]);

  return (
    <section className="scene seating">
      <div className="lanterns" aria-hidden>
        <span>🏮</span>
        <span>🏮</span>
        <span>🏮</span>
      </div>
      <div className="chibi-row">
        <div className="chibi waitress">
          <div className="face">👱‍♀️</div>
          <p>Waitress 靚姐</p>
        </div>
        <div className="bubble big">
          {step === "people" ? (
            <>
              <strong>幾多位？</strong>
              <span>How many people?</span>
            </>
          ) : (
            <>
              <strong>飲咩茶？</strong>
              <span>What tea would you like?</span>
            </>
          )}
        </div>
        <div className="chibi npc">
          <div className="face">👜</div>
          <p>隔壁 NPC</p>
          <small>
            {npc.call} 要{npc.tea}
          </small>
        </div>
      </div>

      {step === "people" ? (
        <div className="choice-grid">
          {PARTY_SIZES.map((n) => (
            <button
              key={n}
              type="button"
              className="choice"
              onClick={() => {
                setPartySize(n);
                setStep("tea");
              }}
            >
              <b>{n} 位</b>
              <span>
                {n <= 2 ? "1 order" : n <= 4 ? "2 orders" : n <= 6 ? "3 orders" : "4 orders"}
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="choice-grid teas">
          {TEAS.map((t) => (
            <button
              key={t.id}
              type="button"
              className="choice"
              onClick={() => onDone(partySize ?? 4, t.id)}
            >
              <b>
                {t.emoji} {t.zh}
              </b>
              <span>{t.en}</span>
              <small>{t.hint}</small>
            </button>
          ))}
        </div>
      )}
      {partySize != null && step === "tea" && (
        <p className="muted">{partySize} 位 already seated · 入座 after tea</p>
      )}
    </section>
  );
}

import React, {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useRef,
  useState,
} from "react";

export type BgmTrack =
  | "seating"
  | "table"
  | "waitress"
  | "cart"
  | "callTea"
  | "milkTea"
  | "pineapple";

export type SfxName = "merge" | "pop" | "bell" | "clink" | "win" | "lose";

type AudioApi = {
  muted: boolean;
  volume: number;
  unlocked: boolean;
  setMuted: (v: boolean) => void;
  setVolume: (v: number) => void;
  unlock: () => void;
  playBgm: (track: BgmTrack) => void;
  pauseBgm: () => void;
  resumeBgm: () => void;
  playSfx: (name: SfxName) => void;
};

const AudioContextValue = createContext<AudioApi | null>(null);

const BGM_SRC: Record<BgmTrack, string> = {
  seating: "/audio/bgm-seating.wav",
  table: "/audio/bgm-table.wav",
  waitress: "/audio/bgm-waitress.wav",
  cart: "/audio/bgm-cart.wav",
  callTea: "/audio/bgm-calltea.wav",
  milkTea: "/audio/bgm-milktea.wav",
  pineapple: "/audio/bgm-pineapple.wav",
};

const SFX_SRC: Record<SfxName, string> = {
  merge: "/audio/sfx-merge.wav",
  pop: "/audio/sfx-pop.wav",
  bell: "/audio/sfx-bell.wav",
  clink: "/audio/sfx-clink.wav",
  win: "/audio/sfx-win.wav",
  lose: "/audio/sfx-lose.wav",
};

export function AudioProvider({ children }: { children: React.ReactNode }) {
  const bgmRef = useRef<HTMLAudioElement | null>(null);
  const trackRef = useRef<BgmTrack | null>(null);
  const [muted, setMutedState] = useState(false);
  const [volume, setVolumeState] = useState(0.55);
  const [unlocked, setUnlocked] = useState(false);
  const mutedRef = useRef(muted);
  const volumeRef = useRef(volume);
  mutedRef.current = muted;
  volumeRef.current = volume;

  const applyBgm = useCallback(() => {
    const el = bgmRef.current;
    if (!el) return;
    el.muted = mutedRef.current;
    el.volume = volumeRef.current;
  }, []);

  const unlock = useCallback(() => {
    setUnlocked(true);
    if (!bgmRef.current) {
      const el = new Audio();
      el.loop = true;
      bgmRef.current = el;
    }
    applyBgm();
    const el = bgmRef.current;
    if (el) {
      el.play().catch(() => undefined);
    }
  }, [applyBgm]);

  const playBgm = useCallback(
    (track: BgmTrack) => {
      if (!bgmRef.current) {
        const el = new Audio();
        el.loop = true;
        bgmRef.current = el;
      }
      const el = bgmRef.current;
      if (trackRef.current === track && !el.paused) {
        applyBgm();
        return;
      }
      trackRef.current = track;
      el.src = BGM_SRC[track];
      el.loop = true;
      applyBgm();
      if (unlocked || true) {
        el.play().catch(() => undefined);
      }
    },
    [applyBgm, unlocked]
  );

  const pauseBgm = useCallback(() => {
    bgmRef.current?.pause();
  }, []);

  const resumeBgm = useCallback(() => {
    applyBgm();
    bgmRef.current?.play().catch(() => undefined);
  }, [applyBgm]);

  const playSfx = useCallback((name: SfxName) => {
    if (mutedRef.current) return;
    const sfx = new Audio(SFX_SRC[name]);
    sfx.volume = volumeRef.current;
    sfx.play().catch(() => undefined);
  }, []);

  const setMuted = useCallback(
    (v: boolean) => {
      setMutedState(v);
      mutedRef.current = v;
      applyBgm();
    },
    [applyBgm]
  );

  const setVolume = useCallback(
    (v: number) => {
      setVolumeState(v);
      volumeRef.current = v;
      applyBgm();
    },
    [applyBgm]
  );

  const api = useMemo(
    () => ({
      muted,
      volume,
      unlocked,
      setMuted,
      setVolume,
      unlock,
      playBgm,
      pauseBgm,
      resumeBgm,
      playSfx,
    }),
    [muted, volume, unlocked, setMuted, setVolume, unlock, playBgm, pauseBgm, resumeBgm, playSfx]
  );

  return (
    <AudioContextValue.Provider value={api}>{children}</AudioContextValue.Provider>
  );
}

export function useAudio() {
  const ctx = useContext(AudioContextValue);
  if (!ctx) throw new Error("useAudio must be inside AudioProvider");
  return ctx;
}

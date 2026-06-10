/**
 * A3 — Hooks para Storytelling Animation
 *
 * useInView: retorna ref e flag booleana quando o elemento entra na viewport.
 *            Dispara uma única vez (triggerOnce=true por padrão) para evitar
 *            replay intrusivo ao scroll. Respeita prefers-reduced-motion.
 *
 * useCountUp: anima um número numérico de 0 até `target` em `duration` ms
 *             usando requestAnimationFrame com easing cubic-out. Se
 *             prefers-reduced-motion estiver ativo, retorna o valor final.
 */
import { useEffect, useRef, useState } from "react";

interface InViewOpts {
  threshold?: number;
  rootMargin?: string;
  triggerOnce?: boolean;
}

export function useInView<T extends HTMLElement = HTMLDivElement>(
  opts: InViewOpts = {}
): [React.RefObject<T | null>, boolean] {
  const { threshold = 0.15, rootMargin = "0px 0px -40px 0px", triggerOnce = true } = opts;
  const ref = useRef<T>(null);
  const [inView, setInView] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    // Se reduced-motion: considerar sempre visível para renderizar imediatamente
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setInView(true);
      return;
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            setInView(true);
            if (triggerOnce) observer.disconnect();
          } else if (!triggerOnce) {
            setInView(false);
          }
        });
      },
      { threshold, rootMargin }
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, [threshold, rootMargin, triggerOnce]);

  return [ref, inView];
}

interface CountUpOpts {
  duration?: number;
  start?: number;
  /** Se true, anima; se false, retorna direto o target (estático) */
  enabled?: boolean;
  /** Delay antes de começar (ms) */
  delay?: number;
}

export function useCountUp(target: number, opts: CountUpOpts = {}): number {
  const { duration = 1400, start = 0, enabled = true, delay = 0 } = opts;
  const [value, setValue] = useState<number>(enabled ? start : target);
  const rafRef = useRef<number | null>(null);
  const timeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!enabled) {
      setValue(target);
      return;
    }
    const reduced =
      typeof window !== "undefined" &&
      window.matchMedia?.("(prefers-reduced-motion: reduce)").matches;
    if (reduced) {
      setValue(target);
      return;
    }
    // easing cubic-out
    const easeOutCubic = (t: number) => 1 - Math.pow(1 - t, 3);

    const run = () => {
      const t0 = performance.now();
      const tick = () => {
        const elapsed = performance.now() - t0;
        const p = Math.min(elapsed / duration, 1);
        setValue(start + (target - start) * easeOutCubic(p));
        if (p < 1) {
          rafRef.current = requestAnimationFrame(tick);
        }
      };
      rafRef.current = requestAnimationFrame(tick);
    };

    if (delay > 0) {
      timeoutRef.current = setTimeout(run, delay);
    } else {
      run();
    }

    return () => {
      if (rafRef.current) cancelAnimationFrame(rafRef.current);
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [target, duration, start, enabled, delay]);

  return value;
}

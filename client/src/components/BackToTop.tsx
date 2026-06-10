// Botão flutuante "voltar ao topo" — aparece ao scrollar
import { ArrowUp } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "@/lib/utils";

export default function BackToTop() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    const onScroll = () => setShow(window.scrollY > 500);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <button
      aria-label="Voltar ao topo"
      onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
      className={cn(
        "fixed bottom-6 right-6 z-40 w-10 h-10 rounded-full",
        "bg-[color:var(--bg-3)] border border-primary/40 text-primary",
        "hover:bg-primary hover:text-background hover:border-primary",
        "transition-all shadow-lg backdrop-blur-sm",
        "flex items-center justify-center no-print",
        show ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none"
      )}
    >
      <ArrowUp className="h-4 w-4" />
    </button>
  );
}

// Command Palette — Cmd+K / Ctrl+K
// Navegação por busca entre as 24+ seções do dashboard DETRAN/AM
import { useEffect, useState } from "react";
import { Command } from "cmdk";
import { NAV_SECTIONS } from "@/data/types";

interface Props {
  onSelect: (sectionId: string) => void;
}

export default function CommandPalette({ onSelect }: Props) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState("");

  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if ((e.key === "k" || e.key === "K") && (e.metaKey || e.ctrlKey)) {
        e.preventDefault();
        setOpen((o) => !o);
      }
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("keydown", down);
    return () => document.removeEventListener("keydown", down);
  }, []);

  if (!open) return null;

  const handleSelect = (id: string) => {
    onSelect(id);
    setOpen(false);
    setQuery("");
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center pt-[15vh] bg-black/70 backdrop-blur-sm print:hidden"
      onClick={() => setOpen(false)}
    >
      <Command
        shouldFilter={true}
        className="w-[min(640px,92vw)] rounded-lg border border-[color:var(--gold)]/40 bg-[color:var(--card)] shadow-2xl overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="flex items-center border-b border-border px-4">
          <svg
            className="mr-2 h-4 w-4 text-[color:var(--gold)]"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
            viewBox="0 0 24 24"
          >
            <circle cx="11" cy="11" r="8" />
            <path d="m21 21-4.3-4.3" />
          </svg>
          <Command.Input
            value={query}
            onValueChange={setQuery}
            placeholder="Buscar seção, contrato, fatura ou termo jurídico…"
            className="flex-1 h-12 bg-transparent text-sm text-foreground placeholder:text-muted-foreground outline-none font-sans"
          />
          <kbd className="ml-2 pointer-events-none select-none rounded border border-border bg-muted/30 px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
            ESC
          </kbd>
        </div>

        <Command.List className="max-h-[60vh] overflow-auto p-2">
          <Command.Empty className="py-8 text-center text-xs text-muted-foreground">
            Nenhum resultado encontrado.
          </Command.Empty>

          {NAV_SECTIONS.map((group) => (
            <Command.Group
              key={group.group}
              heading={group.group}
              className="[&_[cmdk-group-heading]]:px-2 [&_[cmdk-group-heading]]:py-1 [&_[cmdk-group-heading]]:text-[10px] [&_[cmdk-group-heading]]:uppercase [&_[cmdk-group-heading]]:tracking-wider [&_[cmdk-group-heading]]:text-[color:var(--gold)]/70 [&_[cmdk-group-heading]]:font-mono"
            >
              {group.items.map((item) => (
                <Command.Item
                  key={item.id}
                  value={`${group.group} ${item.label} ${item.id}`}
                  onSelect={() => handleSelect(item.id)}
                  className="flex items-center justify-between px-3 py-2 text-[13px] rounded cursor-pointer aria-selected:bg-[color:var(--gold)]/15 aria-selected:text-foreground text-muted-foreground font-sans"
                >
                  <span className="truncate">{item.label}</span>
                  {item.badge && (
                    <span className="ml-3 rounded border border-[color:var(--gold)]/30 bg-[color:var(--gold)]/10 px-1.5 py-0.5 text-[9px] font-mono text-[color:var(--gold)]">
                      {item.badge}
                    </span>
                  )}
                </Command.Item>
              ))}
            </Command.Group>
          ))}
        </Command.List>

        <div className="flex items-center justify-between border-t border-border px-3 py-2 text-[10px] text-muted-foreground font-mono">
          <span>
            <kbd className="rounded border border-border bg-muted/30 px-1 py-0.5">↑</kbd>{" "}
            <kbd className="rounded border border-border bg-muted/30 px-1 py-0.5">↓</kbd>{" "}
            navegar
          </span>
          <span>
            <kbd className="rounded border border-border bg-muted/30 px-1 py-0.5">↵</kbd> abrir
          </span>
          <span>
            <kbd className="rounded border border-border bg-muted/30 px-1 py-0.5">⌘K</kbd> fechar
          </span>
        </div>
      </Command>
    </div>
  );
}

import { useEffect, useState } from "react";
import { TridentCard } from "@/components/trident/TridentCard";

type Col = "now" | "next" | "later";

interface Card {
  id: string;
  title: string;
  status?: string;
  eta: string;
}

const DEFAULT: Record<Col, Card[]> = {
  now: [
    { id: "n1", title: "Wire FlowScore into personalizer", status: "in_progress", eta: "tonight" },
    { id: "n2", title: "Variant B 3-split tests (B1/B2/B3)", status: "in_progress", eta: "tonight" },
    { id: "n3", title: "Variant D Friday rollout", status: "scheduled", eta: "Fri 4am ET" },
    { id: "n4", title: "Persistent Cloudflare tunnel for webhooks", status: "todo", eta: "this week" },
  ],
  next: [
    { id: "x1", title: "Expand ICP filter to 25+ niches", eta: "this week" },
    { id: "x2", title: "Reddit + Twitter + Meta signal sources", eta: "next week" },
    { id: "x3", title: "Persona signature photos in emails", eta: "Mon" },
    { id: "x4", title: "Pre-call brief auto-gen", eta: "next week" },
    { id: "x5", title: "Acquisity full integration", eta: "this week" },
  ],
  later: [
    { id: "l1", title: "n8n migration of Cara enrichment chain", eta: "3 wks" },
    { id: "l2", title: "assets.flowoperations.ai custom domain", eta: "2 wks" },
    { id: "l3", title: "Auto-send for high-confidence replies", eta: "3 wks" },
    { id: "l4", title: "Per-variant Council weight tuning", eta: "4 wks" },
    { id: "l5", title: "Multi-tenant: first 3 client campaigns", eta: "4 wks" },
  ],
};

const COL_META: Record<Col, { label: string; color: string }> = {
  now: { label: "NOW · in progress", color: "hsl(var(--green))" },
  next: { label: "NEXT · 1–2 wks", color: "hsl(var(--amber))" },
  later: { label: "LATER · 3–4 wks", color: "#A855F7" },
};

const STORAGE_KEY = "flowops.cold-email.projects.v1";

export const ProjectsBoard = () => {
  const [board, setBoard] = useState<Record<Col, Card[]>>(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) return JSON.parse(raw);
    } catch {}
    return DEFAULT;
  });
  const [dragId, setDragId] = useState<string | null>(null);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(board));
  }, [board]);

  const move = (cardId: string, target: Col) => {
    setBoard(prev => {
      const next: Record<Col, Card[]> = { now: [...prev.now], next: [...prev.next], later: [...prev.later] };
      let card: Card | undefined;
      (Object.keys(next) as Col[]).forEach(c => {
        const idx = next[c].findIndex(x => x.id === cardId);
        if (idx >= 0) {
          card = next[c][idx];
          next[c].splice(idx, 1);
        }
      });
      if (card) next[target].push(card);
      return next;
    });
  };

  return (
    <div>
      <div className="font-mono text-[10px] text-foreground-tertiary tracking-wider mb-3">PROJECTS BOARD</div>
      <div className="grid grid-cols-3 gap-3">
        {(Object.keys(board) as Col[]).map(col => (
          <div
            key={col}
            onDragOver={e => e.preventDefault()}
            onDrop={() => dragId && move(dragId, col)}
          >
            <TridentCard accentColor={COL_META[col].color}>
              <div className="font-mono text-[10px] tracking-wider mb-3" style={{ color: COL_META[col].color }}>
                {COL_META[col].label}
              </div>
              <div className="space-y-2">
                {board[col].map(card => (
                  <div
                    key={card.id}
                    draggable
                    onDragStart={() => setDragId(card.id)}
                    onDragEnd={() => setDragId(null)}
                    className="p-2.5 rounded bg-background-tertiary/40 border border-border/40 cursor-grab active:cursor-grabbing hover:border-border transition-colors"
                  >
                    <div className="text-xs text-foreground leading-snug">{card.title}</div>
                    <div className="flex items-center justify-between mt-2">
                      {card.status ? (
                        <span className="font-mono text-[9px] px-1.5 py-0.5 rounded"
                          style={{ background: COL_META[col].color + "20", color: COL_META[col].color }}>
                          {card.status.replace("_", " ")}
                        </span>
                      ) : <span />}
                      <span className="font-mono text-[9px] text-foreground-tertiary">{card.eta}</span>
                    </div>
                  </div>
                ))}
                {board[col].length === 0 && (
                  <div className="text-xs text-foreground-tertiary text-center py-4">drop a card here</div>
                )}
              </div>
            </TridentCard>
          </div>
        ))}
      </div>
    </div>
  );
};
type CellValue = string | { text: string; color: string };

interface Props {
  headers: string[];
  rows: CellValue[][];
}

export const DataTable = ({ headers, rows }: Props) => (
  <div className="overflow-x-auto">
    <table className="w-full border-collapse text-[13px]">
      <thead>
        <tr className="bg-background-tertiary">
          {headers.map((h, i) => (
            <th key={i} className="px-3 py-2 text-left text-primary font-bold border-b border-border text-[11px] tracking-wider">{h}</th>
          ))}
        </tr>
      </thead>
      <tbody>
        {rows.map((row, ri) => (
          <tr key={ri} className={ri % 2 === 0 ? "bg-background" : "bg-background-secondary"}>
            {row.map((cell, ci) => {
              const isObj = typeof cell === "object" && cell !== null;
              return (
                <td
                  key={ci}
                  className="px-3 py-2 border-b border-border/10"
                  style={{ color: isObj ? cell.color : undefined, fontWeight: isObj ? 700 : 400 }}
                >
                  <span className={!isObj ? "text-foreground-secondary" : undefined}>
                    {isObj ? (cell as { text: string; color: string }).text : (cell as string)}
                  </span>
                </td>
              );
            })}
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

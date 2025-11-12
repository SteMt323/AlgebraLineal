import React from 'react';

type ResultPrettyProps = { result: any };

const MatrixTable: React.FC<{ matrix: string[][] }> = ({ matrix }) => {
  const cols = matrix[0]?.length ?? 0;
  const lastCol = Math.max(0, cols - 1);
  return (
    <div className="overflow-auto">
      <table className="border-collapse table-auto text-sm">
        <tbody>
          {matrix.map((row, i) => (
            <tr key={i}>
              {row.map((cell, j) => (
                <td
                  key={j}
                  className={`px-3 py-1 border border-white/10 ${j === lastCol ? 'border-l-2 border-white/20' : ''}`}
                >
                  <div className="whitespace-nowrap text-xs text-purple-100">{cell}</div>
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export const ResultPretty: React.FC<ResultPrettyProps> = ({ result }) => {
  if (!result) return null;

  // steps can be either an array of step objects/strings (legacy) or an
  // object for complex operations like inverse: { frame: { ... }, text_steps: [...] }
  const rawSteps = result.steps;
  const stepsArray = Array.isArray(rawSteps) ? rawSteps : (rawSteps?.text_steps ?? []);
  const frame = rawSteps && !Array.isArray(rawSteps) ? rawSteps.frame ?? null : null;
  const summary = result.summary ?? result.result?.summary ?? null;

  // render a single textual step (string) optionally aligned with a matrix snapshot
  const renderTextStepWithMatrix = (text: string, idx: number) => {
    // try to find an aligned matrix snapshot: prefer frame.step_states, fall back to frame.states
    const snap = frame?.step_states?.[idx] ?? frame?.states?.[idx] ?? null;
    const matrix = snap?.matrix ?? null;
    return (
      <div key={idx} className="mb-4">
        <div className="flex items-center justify-between mb-2">
          <div className="text-sm font-semibold text-blue-200">{text}</div>
          {snap?.tag && <div className="text-xs text-white/60 px-2 py-1 rounded bg-white/3">{snap.tag}</div>}
        </div>

        <div className="p-3 bg-gradient-to-br from-white/3 to-white/2 rounded-lg border border-white/10">
          {matrix ? (
            // matrix may be an augmented matrix (numbers) - try to convert to strings
            <MatrixTable matrix={(matrix as any).map((r: any[]) => r.map((c: any) => String(c)))} />
          ) : (
            <pre className="text-xs text-purple-100">{String(text)}</pre>
          )}
        </div>
      </div>
    );
  };

  const renderParticular = (particularPretty: any, particular: any) => {
    if (particularPretty) {
      if (Array.isArray(particularPretty)) {
        return (
          <ul className="list-disc pl-5">
            {particularPretty.map((v:any, i:number) => (
              <li key={i} className="text-xs">{`x${i+1} = ${v ?? '0'}`}</li>
            ))}
          </ul>
        );
      }
      return <pre className="text-xs">{String(particularPretty)}</pre>;
    }

    if (particular) {
      if (Array.isArray(particular)) {
        return (
          <ul className="list-disc pl-5">
            {particular.map((v:number, i:number) => (
              <li key={i} className="text-xs">{`x${i+1} = ${v}`}</li>
            ))}
          </ul>
        );
      }
      return <pre className="text-xs">{JSON.stringify(particular, null, 2)}</pre>;
    }

    return null;
  };

  const renderSummary = (sm: any) => {
    if (!sm) return null;
    const vars = sm.variables ?? sm?.parametric_form?.symbolic?.variables ?? null;
    const basic = sm.variables?.basic ?? sm?.variables?.basic ?? [];
    const free = sm.variables?.free ?? sm?.variables?.free ?? [];
    const particularPretty = sm.parametric_form?.particular_pretty ?? sm.parametric_form?.particular_pretty ?? null;
    const particular = sm.parametric_form?.particular ?? null;

    return (
      <div className="space-y-3">
        <div className="p-3 rounded bg-white/3 border border-white/10">
          <div className="text-sm font-semibold text-blue-200 mb-2">Resumen</div>
          {sm.ranks && (
            <div className="text-xs text-purple-100 mb-2">Rango A: {sm.ranks.rankA}, Rango [A|b]: {sm.ranks.rankAb}</div>
          )}

          <div className="grid grid-cols-3 gap-2 text-xs">
            <div>
              <div className="text-white/70 text-[11px]">Variables básicas</div>
              <div className="text-purple-100">{basic.length ? basic.map((i:number) => `x${i+1}`).join(', ') : '—'}</div>
            </div>
            <div>
              <div className="text-white/70 text-[11px]">Variables libres</div>
              <div className="text-purple-100">{free.length ? free.map((i:number) => `x${i+1}`).join(', ') : '—'}</div>
            </div>

            <div>
              <div className="text-white/70 text-[11px]">Tipo de solución</div>
              <div className="text-purple-100">{sm.solution_type ?? sm?.solution_type ?? '—'}</div>
            </div>
          </div>

          { (particularPretty || particular) && (
            <div className="mt-3">
              <div className="text-white/70 text-[11px]">Solución particular</div>
              <div className="text-purple-100 text-xs mt-1">
                {renderParticular(particularPretty, particular)}
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-4">
      {/* Steps */}
      {stepsArray.length > 0 && (
        <div>
          <div className="text-sm font-semibold text-blue-200 mb-3">Pasos</div>
          <div className="space-y-3">
            {stepsArray.map((s:any, i:number) => (
              // if frame is present, align text_steps with frame snapshots
              frame ? renderTextStepWithMatrix(String(s), i) : (
                <div key={i} className="mb-2">
                  <pre className="text-xs text-purple-100">{String(s)}</pre>
                </div>
              )
            ))}
          </div>
        </div>
      )}

      {/* Result matrix pretty (for sum/sub/matmul/transpose/scalar etc) */}
      {result?.result?.matrix_pretty && (
        <div>
          <div className="text-sm font-semibold text-blue-200 mb-3">Resultado</div>
          <div className="p-3 bg-gradient-to-br from-white/3 to-white/2 rounded-lg border border-white/10">
            <MatrixTable matrix={result.result.matrix_pretty} />
          </div>
        </div>
      )}

      {/* Summary */}
      {summary && (
        <div>
          {renderSummary(summary)}
        </div>
      )}
    </div>
  );
};

export default ResultPretty;

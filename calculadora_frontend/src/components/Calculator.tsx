import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Plus, Minus, X as Multiply, Divide, RotateCw, Calculator as CalcIcon, Grid3x3Icon, Triangle } from 'lucide-react';
import { Button } from './ui/button';
import { MatrixInput } from './inputs/MatrixInput';
import { VectorInput } from './inputs/VectorInput';
import { DigitalKeyboard } from './DigitalKeyboard';
import EscalarInput from './inputs/EscalarInput';
import { OperationSelector } from './OperationSelector';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import parseCellInput from '../utils/parseInput';
import { matrixOperate, matrixDeterminant, matrixReduce, vectorOperate, vectorCombination } from '../api/client';
import ResultPretty from './Output/ResultPretty';

  // Map frontend operation ids to backend expected operation strings
  function mapMatrixOperation(opId: string) {
    const m: Record<string, string> = {
      // single-pair operations removed: use many-versions only
      scalar_mult: 'scalar',
      //scalar: 'scalar',
      transpose: 'transpose',
      inverse: 'inverse',
      sum_many: 'sum_many',
      sub_many: 'sub_many',
      matmul_chain: 'matmul_chain',
    };
    return m[opId] || opId;
  }

  function mapVectorOperation(opId: string) {
    const m: Record<string, string | null> = {
      add_vectores: 'add',
      sub_vectorers: 'sub',
      dot: 'dot',
      scalar_vect: 'escalar',
      comb2: 'comb2',
      comb3: 'comb3',
      // 'linear_combination' handled separately
    };
    return m[opId] ?? null;
  }

interface CalculatorProps {
  onBack: () => void;
}

export type MatrixValue = (string | number)[][];
export type VectorValue = (string | number)[];

type InputMode = 'matrix' | 'vector' | 'reduce' | 'determinant';

export function Calculator({ onBack }: CalculatorProps) {
  const [inputMode, setInputMode] = useState<InputMode>('matrix');
  
  // Matrix state
  const [matrixA, setMatrixA] = useState<MatrixValue>([[0, 0], [0, 0]]);
  const [matrixB, setMatrixB] = useState<MatrixValue>([[0, 0], [0, 0]]);
  const [dimensionsA, setDimensionsA] = useState({ rows: 2, cols: 2 });
  const [dimensionsB, setDimensionsB] = useState({ rows: 2, cols: 2 });
  const [selectedMatrixCell, setSelectedMatrixCell] = useState<{ 
    matrix: 'A' | 'B'; 
    row: number; 
    col: number 
  } | null>(null);
  
  // Vector state
  const [vectorA, setVectorA] = useState<VectorValue>([0, 0, 0]);
  const [vectorB, setVectorB] = useState<VectorValue>([0, 0, 0]);
  const [dimensionVectorA, setDimensionVectorA] = useState(3);
  const [dimensionVectorB, setDimensionVectorB] = useState(3);
  const [selectedVectorCell, setSelectedVectorCell] = useState<{ 
    vector: 'A' | 'B'; 
    index: number 
  } | null>(null);

  // scalar selection state (for EscalarInput)
  const [selectedScalar, setSelectedScalar] = useState<boolean>(false);

  const [operation, setOperation] = useState<string>('sum_many');
  const [manyCount, setManyCount] = useState<number>(2);
  const [manyMatrices, setManyMatrices] = useState<MatrixValue[]>(() => {
    return [
      Array(2).fill(0).map(() => Array(2).fill(0)),
      Array(2).fill(0).map(() => Array(2).fill(0)),
    ];
  });
  const [manyMatricesErrors, setManyMatricesErrors] = useState<Record<string, string>[]>([]);

  // scalar input for scalar multiplication (string so parser can accept pi, fractions...)
  const [scalarInput, setScalarInput] = useState<string>('1');
  const [scalarError, setScalarError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [lastResult, setLastResult] = useState<any | null>(null);

  useEffect(() => {
    const raw = localStorage.getItem('calc_last_result');
    if (raw) {
      try {
        setLastResult(JSON.parse(raw));
      } catch (e) {
        // ignore
      }
    }
  }, []);

  const handleKeyPress = (value: string) => {
    // Prefer writing to a selected scalar if present
    if (selectedScalar) {
      const currentValue = String(scalarInput);
      if (value === 'backspace') {
        setScalarInput(currentValue.length > 1 ? currentValue.slice(0, -1) : '0');
      } else if (value === 'clear') {
        setScalarInput('0');
      } else if (value === '+/-') {
        setScalarInput(currentValue.startsWith('-') ? currentValue.slice(1) : '-' + currentValue);
      } else {
        setScalarInput(currentValue === '0' ? value : currentValue + value);
      }
      return;
    }

    // Prefer writing to a selected vector cell if present (covers vector mode and reduce's vector B)
    if (selectedVectorCell) {
      const { vector: vectorName, index } = selectedVectorCell;
      const vector = vectorName === 'A' ? vectorA : vectorB;
      const setVector = vectorName === 'A' ? setVectorA : setVectorB;

      const newVector = vector.map((val, i) => {
        if (i === index) {
          const currentValue = String(val);
          if (value === 'backspace') {
            return currentValue.length > 1 ? currentValue.slice(0, -1) : '0';
          } else if (value === 'clear') {
            return '0';
          } else if (value === '+/-') {
            return currentValue.startsWith('-') ? currentValue.slice(1) : '-' + currentValue;
          } else {
            return currentValue === '0' ? value : currentValue + value;
          }
        }
        return val;
      });

      setVector(newVector);
      return;
    }

    // Otherwise write to selected matrix cell (covers matrix/reduce/determinant)
    if (selectedMatrixCell) {
      const { matrix: matrixName, row, col } = selectedMatrixCell;
      const matrix = matrixName === 'A' ? matrixA : matrixB;
      const setMatrix = matrixName === 'A' ? setMatrixA : setMatrixB;

      const newMatrix = matrix.map((r, i) =>
        r.map((c, j) => {
          if (i === row && j === col) {
            const currentValue = String(c);
            if (value === 'backspace') {
              return currentValue.length > 1 ? currentValue.slice(0, -1) : '0';
            } else if (value === 'clear') {
              return '0';
            } else if (value === '+/-') {
              return currentValue.startsWith('-') ? currentValue.slice(1) : '-' + currentValue;
            } else {
              return currentValue === '0' ? value : currentValue + value;
            }
          }
          return c;
        })
      );

      setMatrix(newMatrix);
    }
  };

  const handleMatrixCellChange = (matrixName: 'A' | 'B', row: number, col: number, newValue: string) => {
    const setter = matrixName === 'A' ? setMatrixA : setMatrixB;
    const matrix = matrixName === 'A' ? matrixA : matrixB;
    const newMatrix = matrix.map((r, i) => r.map((c, j) => (i === row && j === col ? newValue : c)));
    // validate
    const parse = parseCellInput(newValue);
    const key = `${row}-${col}`;
    if (matrixName === 'A') {
      if (!parse.valid) {
        setMatrixErrorsA((prev) => ({ ...prev, [key]: parse.error }));
      } else {
        setMatrixErrorsA((prev) => {
          const copy = { ...prev };
          delete copy[key];
          return copy;
        });
      }
    } else {
      if (!parse.valid) {
        setMatrixErrorsB((prev) => ({ ...prev, [key]: parse.error }));
      } else {
        setMatrixErrorsB((prev) => {
          const copy = { ...prev };
          delete copy[key];
          return copy;
        });
      }
    }

    setter(newMatrix);
  };

  // Many-matrices handlers
  const manyOps = ['sum_many', 'sub_many', 'matmul_chain'];

  const clampManyCount = (n: number) => Math.max(2, Math.min(6, n));

  const handleManyCountChange = (n: number) => {
    const next = clampManyCount(n);
    setManyCount(next);
    setManyMatrices((prev) => {
      const copy = [...prev];
      if (next > copy.length) {
        for (let i = copy.length; i < next; i++) {
          copy.push(Array(2).fill(0).map(() => Array(2).fill(0)));
        }
      } else if (next < copy.length) {
        copy.length = next;
      }
      return copy;
    });
    setManyMatricesErrors((prev) => {
      const copy = [...prev];
      if (next > copy.length) {
        for (let i = copy.length; i < next; i++) copy.push({});
      } else if (next < copy.length) copy.length = next;
      return copy;
    });
  };

  const handleManyMatrixCellChange = (idx: number, row: number, col: number, newValue: string) => {
    setManyMatrices((prev) => {
      const copy = prev.map((m) => m.map((r) => [...r]));
      const matrix = copy[idx];
      matrix[row][col] = newValue;
      return copy;
    });

    // validate
    const parsed = parseCellInput(newValue);
    setManyMatricesErrors((prev) => {
      const copy = prev.length ? prev.map((p) => ({ ...p })) : Array(manyCount).fill({}).map(() => ({}));
      const key = `${row}-${col}`;
      if (!parsed.valid) {
        copy[idx] = { ...(copy[idx] || {}), [key]: parsed.error || 'Invalid' };
      } else {
        if (!copy[idx]) copy[idx] = {};
        const c = { ...copy[idx] };
        delete c[key];
        copy[idx] = c;
      }
      return copy;
    });
  };

  const handleVectorCellChange = (vectorName: 'A' | 'B', index: number, newValue: string) => {
    const setter = vectorName === 'A' ? setVectorA : setVectorB;
    const vector = vectorName === 'A' ? vectorA : vectorB;
    const newVector = vector.map((v, i) => (i === index ? newValue : v));
    const parse = parseCellInput(newValue);
    const key = String(index);
    if (vectorName === 'A') {
      if (!parse.valid) setVectorErrorsA((prev) => ({ ...prev, [key]: parse.error }));
      else setVectorErrorsA((prev) => { const copy = { ...prev }; delete copy[key]; return copy; });
    } else {
      if (!parse.valid) setVectorErrorsB((prev) => ({ ...prev, [key]: parse.error }));
      else setVectorErrorsB((prev) => { const copy = { ...prev }; delete copy[key]; return copy; });
    }

    setter(newVector);
  };

  // validation error maps
  const [matrixErrorsA, setMatrixErrorsA] = useState<Record<string, string>>({});
  const [matrixErrorsB, setMatrixErrorsB] = useState<Record<string, string>>({});
  const [vectorErrorsA, setVectorErrorsA] = useState<Record<string, string>>({});
  const [vectorErrorsB, setVectorErrorsB] = useState<Record<string, string>>({});

  // Matrix operations mapped to backend implementations in algebra/algorithms/matrix/matrix_operations.py
  const matrixOperations = [
    { id: 'sum_many', label: 'A + B + ..', icon: Plus, description: 'Suma de varias matrices' },
    { id: 'sub_many', label: 'A - B + ..', icon: Minus, description: 'Resta de varias matrices' },
    { id: 'matmul_chain', label: 'A · B · ...', icon: Multiply, description: 'Cadena de multiplicaciones' },
    { id: 'scalar_mult', label: 'k · A', icon: Multiply, description: 'Multiplicación escalar' },
    { id: 'transpose', label: 'Aᵀ', icon: RotateCw, description: 'Transponer A', single: true },
    { id: 'inverse', label: 'A⁻¹', icon: Grid3x3Icon, description: 'Matriz inversa', single: true },
  ];

  // Vector operations (from algebra/algorithms/vectors)
  const vectorOperations = [
    { id: 'add_vectores', label: 'A + B', icon: Plus, description: 'Suma de vectores' },
    { id: 'sub_vectores', label: 'A - B', icon: Minus, description: 'Resta de vectores' },
    { id: 'dot', label: 'A · B', icon: Multiply, description: 'Producto escalar' },
    { id: 'scalar_vect', label: 'k · A', icon: Multiply, description: 'Multiplicación escalar', single: true },
    { id: 'comb2', label: 'c·u + d·v', icon: Plus, description: 'Combinación lineal (2 vectores)' },
    { id: 'comb3', label: 'u + c·v + d·w', icon: Plus, description: 'Combinación lineal (3 vectores)' },
    { id: 'linear_combination', label: 'Combinación lineal (Ax = b)', icon: Plus, description: 'Verificar/obtener combinación lineal' },
  ];

  // Reduction methods (sistema de ecuaciones)
  const reduceOperations = [
    { id: 'gauss', label: 'Eliminación Gauss', icon: Grid3x3Icon, description: 'Eliminación gaussiana (forward/backward)', single: false },
    { id: 'gauss_jordan', label: 'Gauss-Jordan', icon: RotateCw, description: 'Eliminación Gauss-Jordan (forma reducida)', single: false },
  ];

  // Determinant calculation methods (match docs: Gauss, Gauss-Jordan, Cramer)
  const determinantMethods = [
    { id: 'sarrus', label: 'Sarrus-Method', icon: Grid3x3Icon, description: 'Cálculo de determinante por método de Sarrus', single: true },
    { id: 'cofactors', label: 'Cofactors-Method', icon: RotateCw, description: 'Cálculo del determinante por expansión de Cofactores', single: true },
    { id: 'cramer', label: 'Cramer', icon: CalcIcon, description: 'Cálculo por regla de Cramer (sólo para sistemas cuadrados)', single: true },
  ];

  const getOperationsForMode = (mode: InputMode) => {
    if (mode === 'matrix') return matrixOperations;
    if (mode === 'vector') return vectorOperations;
    if (mode === 'reduce') return reduceOperations;
    if (mode === 'determinant') return determinantMethods;
  };

  const currentOperations = getOperationsForMode(inputMode);
  const selectedOperation = currentOperations.find(op => op.id === operation);

  // when operation changes, clear scalar selection unless scalar_mult is active
  useEffect(() => {
    if (operation !== 'scalar_mult') setSelectedScalar(false);
  }, [operation]);

  let needsTwoInputs: boolean;
  if (inputMode === 'reduce') {
    // systems: always need matrix A and vector b
    needsTwoInputs = true;
  } else if (inputMode === 'determinant') {
    // determinant: only matrix A
    needsTwoInputs = false;
  } else {
    needsTwoInputs = !selectedOperation?.single;
  }

  return (
    <div className="min-h-screen relative overflow-hidden p-4 md:p-8">
      {/* Animated background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <motion.div
          className="absolute inset-0 opacity-5"
          style={{
            backgroundImage: `linear-gradient(rgba(99, 102, 241, 0.4) 1px, transparent 1px),
                            linear-gradient(90deg, rgba(99, 102, 241, 0.4) 1px, transparent 1px)`,
            backgroundSize: '40px 40px',
          }}
          animate={{
            backgroundPosition: ['0px 0px', '40px 40px'],
          }}
          transition={{
            duration: 15,
            repeat: Infinity,
            ease: 'linear',
          }}
        />

        {/* Glowing orbs */}
        <motion.div
          className="absolute top-20 left-20 w-72 h-72 bg-blue-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, 50, 0],
            y: [0, 30, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
          }}
        />
        <motion.div
          className="absolute bottom-20 right-20 w-72 h-72 bg-purple-500/10 rounded-full blur-3xl"
          animate={{
            x: [0, -50, 0],
            y: [0, -30, 0],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: 'easeInOut',
            delay: 1,
          }}
        />
      </div>

      {/* Header */}
      <motion.div
        className="relative z-10 mb-6"
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-4 flex items-center justify-between">
          <Button
            onClick={onBack}
            variant="ghost"
            className="text-blue-200 hover:text-blue-100 hover:bg-white/10"
          >
            <ArrowLeft className="mr-2" size={20} />
            Volver
          </Button>
          <div className="flex items-center gap-3">
            <CalcIcon className="text-purple-300" size={24} />
            <h2 className="text-2xl bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">
              LinealCalc
            </h2>
          </div>
          <div className="w-24" />
        </div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto">
        {/* Mode Selector */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mb-6"
        >
          <Tabs 
            value={inputMode} 
            onValueChange={(v) => {
                const mode = v as InputMode;
                setInputMode(mode);
                const ops = getOperationsForMode(mode);
                setOperation(ops[0]?.id ?? ''); // Reset operation to first available for the mode
              setSelectedMatrixCell(null);
              setSelectedVectorCell(null);
              setSelectedScalar(false);
            }}
            className="w-full"
          >
            <TabsList className="grid w-full mx-auto grid-cols-4 backdrop-blur-xl bg-white/5 border border-white/10 h-14">
              <TabsTrigger 
                value="matrix" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 text-base"
              >
                <Grid3x3Icon className="w-5 h-5 mr-2" />
                Matrices
              </TabsTrigger>

              <TabsTrigger 
                value="reduce" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-pink-600 text-base"
              >
                <Triangle className="w-5 h-5 mr-2" />
                Sistema de Ecuaciones
              </TabsTrigger>

              <TabsTrigger 
                value="determinant" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 text-base"
              >
                <Triangle className="w-5 h-5 mr-2" />
                Determinantes
              </TabsTrigger>

              <TabsTrigger 
                value="vector" 
                className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-pink-600 text-base"
              >
                <Triangle className="w-5 h-5 mr-2" />
                Vectores
              </TabsTrigger>
            </TabsList>
          </Tabs>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left Column - Inputs */}
          <div className="lg:col-span-2 space-y-6">
            {/* Operation Selector */}
            <OperationSelector
              operations={currentOperations}
              selectedOperation={operation}
              onSelectOperation={setOperation}
            />

            {/* Inputs */}
            <AnimatePresence mode="wait">
              {inputMode === 'matrix' ? (
                <motion.div
                  key="matrix-inputs"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-6"
                >
                  {operation === 'scalar_mult' ? (
                    <div className="col-span-2 space-y-4">
                      <MatrixInput
                        label="Matriz A"
                        matrix={matrixA}
                        dimensions={dimensionsA}
                        isSelected={selectedMatrixCell?.matrix === 'A'}
                        selectedCell={selectedMatrixCell?.matrix === 'A' ? { row: selectedMatrixCell.row, col: selectedMatrixCell.col } : null}
                        onSelectMatrix={() => {}}
                        onSelectCell={(row, col) => {
                          setSelectedMatrixCell({ matrix: 'A', row, col });
                          setSelectedVectorCell(null);
                          setSelectedScalar(false);
                        }}
                        onCellChange={(r, c, v) => handleMatrixCellChange('A', r, c, v)}
                        errors={matrixErrorsA}
                        onDimensionsChange={(rows, cols) => {
                          setDimensionsA({ rows, cols });
                          const newMatrix = Array(rows)
                            .fill(0)
                            .map(() => Array(cols).fill(0));
                          setMatrixA(newMatrix);
                          setMatrixErrorsA({});
                          setSelectedMatrixCell(null);
                        }}
                      />

                      <EscalarInput
                        value={scalarInput}
                        onChange={(v) => { setScalarInput(v); setScalarError(null); }}
                        onSelect={() => { setSelectedScalar(true); setSelectedMatrixCell(null); setSelectedVectorCell(null); }}
                        onBlur={() => setSelectedScalar(false)}
                        isSelected={selectedScalar}
                        label="Escalar k"
                      />
                    </div>
                  ) : manyOps.includes(operation) ? (
                    <div className="col-span-2 space-y-4">
                      <div className="flex items-center gap-3">
                        <label className="text-sm text-purple-200">Número de matrices:</label>
                        <input
                          type="number"
                          min={2}
                          max={6}
                          value={manyCount}
                          onChange={(e) => handleManyCountChange(Number(e.target.value || 2))}
                          className="bg-white/5 border border-white/10 rounded px-2 py-1 w-20"
                        />
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {manyMatrices.map((M, idx) => (
                          <MatrixInput
                            key={`many-${idx}`}
                            label={`Matriz ${idx + 1}`}
                            matrix={M}
                            dimensions={{ rows: M.length, cols: M[0]?.length ?? 0 }}
                            isSelected={false}
                            selectedCell={null}
                            onSelectMatrix={() => {}}
                            onSelectCell={(row, col) => {
                              // avoid mapping many-matrices cell selection to A/B; clear global selections
                              setSelectedMatrixCell(null);
                              setSelectedVectorCell(null);
                            }}
                            onCellChange={(r, c, v) => handleManyMatrixCellChange(idx, r, c, v)}
                            errors={manyMatricesErrors[idx] || {}}
                            onDimensionsChange={(rows, cols) => {
                              setManyMatrices((prev) => {
                                const copy = prev.map((m) => m.map((r) => [...r]));
                                const newM = Array(rows).fill(0).map(() => Array(cols).fill(0));
                                copy[idx] = newM;
                                return copy;
                              });
                            }}
                          />
                        ))}
                      </div>
                    </div>
                  ) : (
                    <>
                      <MatrixInput
                        label="Matriz A"
                        matrix={matrixA}
                        dimensions={dimensionsA}
                        isSelected={selectedMatrixCell?.matrix === 'A'}
                        selectedCell={selectedMatrixCell?.matrix === 'A' ? { row: selectedMatrixCell.row, col: selectedMatrixCell.col } : null}
                        onSelectMatrix={() => {}}
                        onSelectCell={(row, col) => {
                          setSelectedMatrixCell({ matrix: 'A', row, col });
                          setSelectedVectorCell(null);
                          setSelectedScalar(false);
                        }}
                        onCellChange={(r, c, v) => handleMatrixCellChange('A', r, c, v)}
                        errors={matrixErrorsA}
                        onDimensionsChange={(rows, cols) => {
                          setDimensionsA({ rows, cols });
                          const newMatrix = Array(rows)
                            .fill(0)
                            .map(() => Array(cols).fill(0));
                          setMatrixA(newMatrix);
                          setMatrixErrorsA({});
                          setSelectedMatrixCell(null);
                        }}
                      />

                      {needsTwoInputs && (
                        <MatrixInput
                          label="Matriz B"
                          matrix={matrixB}
                          dimensions={dimensionsB}
                          isSelected={selectedMatrixCell?.matrix === 'B'}
                          selectedCell={selectedMatrixCell?.matrix === 'B' ? { row: selectedMatrixCell.row, col: selectedMatrixCell.col } : null}
                          onSelectMatrix={() => {}}
                          onSelectCell={(row, col) => {
                            setSelectedMatrixCell({ matrix: 'B', row, col });
                            setSelectedVectorCell(null);
                            setSelectedScalar(false);
                          }}
                            onCellChange={(r, c, v) => handleMatrixCellChange('B', r, c, v)}
                            errors={matrixErrorsB}
                          onDimensionsChange={(rows, cols) => {
                            setDimensionsB({ rows, cols });
                            const newMatrix = Array(rows)
                              .fill(0)
                              .map(() => Array(cols).fill(0));
                            setMatrixB(newMatrix);
                            setMatrixErrorsB({});
                            setSelectedMatrixCell(null);
                          }}
                        />
                      )}
                    </>
                  )}
                </motion.div>
              ) : inputMode === 'vector' ? (
                <motion.div
                  key="vector-inputs"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-6"
                >
                  <VectorInput
                    label="Vector A"
                    vector={vectorA}
                    dimension={dimensionVectorA}
                    isSelected={selectedVectorCell?.vector === 'A'}
                    selectedIndex={selectedVectorCell?.vector === 'A' ? selectedVectorCell.index : null}
                    onSelectVector={() => {}}
                    onSelectCell={(index) => {
                      setSelectedVectorCell({ vector: 'A', index });
                      setSelectedMatrixCell(null);
                    }}
                    onCellChange={(idx, v) => handleVectorCellChange('A', idx, v)}
                    errors={vectorErrorsA}
                    onDimensionChange={(dim) => {
                      setDimensionVectorA(dim);
                      const newVector = Array(dim).fill(0);
                      setVectorA(newVector);
                      setVectorErrorsA({});
                      setSelectedVectorCell(null);
                    }}
                  />

                  {needsTwoInputs && (
                    <VectorInput
                      label="Vector B"
                      vector={vectorB}
                      dimension={dimensionVectorB}
                      isSelected={selectedVectorCell?.vector === 'B'}
                      selectedIndex={selectedVectorCell?.vector === 'B' ? selectedVectorCell.index : null}
                      onSelectVector={() => {}}
                      onSelectCell={(index) => {
                        setSelectedVectorCell({ vector: 'A', index });
                        setSelectedMatrixCell(null);
                        setSelectedScalar(false);
                      }}
                        onCellChange={(idx, v) => handleVectorCellChange('B', idx, v)}
                        errors={vectorErrorsB}
                      onDimensionChange={(dim) => {
                        setDimensionVectorB(dim);
                        const newVector = Array(dim).fill(0);
                        setVectorB(newVector);
                        setVectorErrorsB({});
                        setSelectedVectorCell(null);
                      }}
                    />
                  )}
                </motion.div>
              ) : inputMode === 'reduce' ? (
                <motion.div
                  key="reduce-inputs"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="grid grid-cols-1 md:grid-cols-2 gap-6"
                >
                  <MatrixInput
                    label="Matriz A"
                    matrix={matrixA}
                    dimensions={dimensionsA}
                    isSelected={selectedMatrixCell?.matrix === 'A'}
                    selectedCell={selectedMatrixCell?.matrix === 'A' ? { row: selectedMatrixCell.row, col: selectedMatrixCell.col } : null}
                    onSelectMatrix={() => {}}
                    onSelectCell={(row, col) => {
                      setSelectedMatrixCell({ matrix: 'A', row, col });
                      setSelectedVectorCell(null);
                    }}
                    onCellChange={(r, c, v) => handleMatrixCellChange('A', r, c, v)}
                    errors={matrixErrorsA}
                    onDimensionsChange={(rows, cols) => {
                      setDimensionsA({ rows, cols });
                      const newMatrix = Array(rows)
                        .fill(0)
                        .map(() => Array(cols).fill(0));
                      setMatrixA(newMatrix);
                      setMatrixErrorsA({});
                      setSelectedMatrixCell(null);
                    }}
                  />

                  <VectorInput
                    label="Vector B (términos independientes)"
                    vector={vectorB}
                    dimension={dimensionVectorB}
                    isSelected={selectedVectorCell?.vector === 'B'}
                    selectedIndex={selectedVectorCell?.vector === 'B' ? selectedVectorCell.index : null}
                    onSelectVector={() => {}}
                    onSelectCell={(index) => {
                        setSelectedVectorCell({ vector: 'B', index });
                        setSelectedMatrixCell(null);
                        setSelectedScalar(false);
                    }}
                    onCellChange={(idx, v) => handleVectorCellChange('B', idx, v)}
                    errors={vectorErrorsB}
                    onDimensionChange={(dim) => {
                      setDimensionVectorB(dim);
                      const newVector = Array(dim).fill(0);
                      setVectorB(newVector);
                      setSelectedVectorCell(null);
                    }}
                  />
                </motion.div>
              ) : (
                /* determinant mode */
                <motion.div
                  key="determinant-inputs"
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  className="grid grid-cols-1 md:grid-cols-1 gap-6"
                >
                  <MatrixInput
                    label="Matriz A"
                    matrix={matrixA}
                    dimensions={dimensionsA}
                    isSelected={selectedMatrixCell?.matrix === 'A'}
                    selectedCell={selectedMatrixCell?.matrix === 'A' ? { row: selectedMatrixCell.row, col: selectedMatrixCell.col } : null}
                    onSelectMatrix={() => {}}
                    onSelectCell={(row, col) => {
                      setSelectedMatrixCell({ matrix: 'A', row, col });
                      setSelectedVectorCell(null);
                    }}
                    onCellChange={(r, c, v) => handleMatrixCellChange('A', r, c, v)}
                    onDimensionsChange={(rows, cols) => {
                      setDimensionsA({ rows, cols });
                      const newMatrix = Array(rows)
                        .fill(0)
                        .map(() => Array(cols).fill(0));
                      setMatrixA(newMatrix);
                      setSelectedMatrixCell(null);
                    }}
                  />
                </motion.div>
              )}
            </AnimatePresence>

            {/* scalar-multiplication UI is handled inside the animated inputs branch above */}

            {/* Result Preview */}
            <motion.div
              className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-xl text-blue-200">Resultado</h3>
                <Button
                  className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700"
                  onClick={async () => {
                    setSubmitError(null);
                    setLoading(true);
                    try {
                      // prepare and validate inputs depending on mode
                      // helper parsers
                      const parseMatrix = (m: MatrixValue) => {
                        const A: number[][] = [];
                        const errors: Record<string, string> = {};
                        m.forEach((row, i) => {
                          const r: number[] = [];
                          row.forEach((cell, j) => {
                            const parsed = parseCellInput(String(cell));
                            const key = `${i}-${j}`;
                            if (!parsed.valid) {
                              errors[key] = parsed.error || 'Invalid';
                              r.push(NaN);
                            } else r.push(parsed.value ?? NaN);
                          });
                          A.push(r);
                        });
                        return { A, errors };
                      };

                      const parseVector = (v: VectorValue) => {
                        const out: number[] = [];
                        const errors: Record<string, string> = {};
                        v.forEach((cell, i) => {
                          const parsed = parseCellInput(String(cell));
                          const key = String(i);
                          if (!parsed.valid) {
                            errors[key] = parsed.error || 'Invalid';
                            out.push(NaN);
                          } else out.push(parsed.value ?? NaN);
                        });
                        return { out, errors };
                      };

                      // perform per-mode handling
                      if (inputMode === 'matrix') {
                        // if operation is determinant, use determinant endpoint
                        if (operation === 'determinant') {
                          const { A, errors } = parseMatrix(matrixA);
                          if (Object.keys(errors).length) {
                            setMatrixErrorsA(errors);
                            setSubmitError('Hay entradas inválidas en la matriz A.');
                            setLoading(false);
                            return;
                          }
                            const res = await matrixDeterminant({ method: 'cofactors', A });
                            localStorage.setItem('calc_last_result', JSON.stringify(res));
                            setLastResult(res);
                            window.dispatchEvent(new Event('calc:updated'));
                          setLoading(false);
                          return;
                        }

                        // general matrix operations using matrixOperate
                        // support many-matrix operations
                        if (manyOps.includes(operation)) {
                          const matricesParsed: number[][][] = [];
                          const allErrors: Record<string, string>[] = [];
                          let anyErr = false;
                          manyMatrices.forEach((m, mi) => {
                            const parsedRes = parseMatrix(m);
                            matricesParsed.push(parsedRes.A);
                            allErrors.push(parsedRes.errors);
                            if (Object.keys(parsedRes.errors).length) anyErr = true;
                          });
                          if (anyErr) {
                            setManyMatricesErrors(allErrors);
                            setSubmitError('Hay entradas inválidas en una o más matrices.');
                            setLoading(false);
                            return;
                          }
                          const payload: any = { operation: mapMatrixOperation(operation), matrices: matricesParsed };
                          const res = await matrixOperate(payload);
                          localStorage.setItem('calc_last_result', JSON.stringify(res));
                          setLastResult(res);
                          window.dispatchEvent(new Event('calc:updated'));
                          setLoading(false);
                          return;
                        }

                        const { A, errors: errA } = parseMatrix(matrixA);
                        let payload: any = { operation: mapMatrixOperation(operation) };
                        if (Object.keys(errA).length) {
                          setMatrixErrorsA(errA);
                          setSubmitError('Hay entradas inválidas en la matriz A.');
                          setLoading(false);
                          return;
                        }
                        payload.A = A;

                        if (operation === 'scalar_mult') {
                          const parsedScalar = parseCellInput(scalarInput);
                          if (!parsedScalar.valid) {
                            setScalarError(parsedScalar.error || 'Invalid scalar');
                            setSubmitError('Escalar inválido');
                            setLoading(false);
                            return;
                          }
                          payload.scalar = parsedScalar.value ?? 0;
                        }

                        if (needsTwoInputs) {
                          const { A: B, errors: errB } = parseMatrix(matrixB);
                          if (Object.keys(errB).length) {
                            setMatrixErrorsB(errB);
                            setSubmitError('Hay entradas inválidas en la matriz B.');
                            setLoading(false);
                            return;
                          }
                          payload.B = B;
                        }

                        const res = await matrixOperate(payload);
                        localStorage.setItem('calc_last_result', JSON.stringify(res));
                        setLastResult(res);
                        window.dispatchEvent(new Event('calc:updated'));
                        setLoading(false);
                        return;
                      }

                      if (inputMode === 'determinant') {
                        const { A, errors } = parseMatrix(matrixA);
                        if (Object.keys(errors).length) {
                          setMatrixErrorsA(errors);
                          setSubmitError('Hay entradas inválidas en la matriz A.');
                          setLoading(false);
                          return;
                        }
                        const res = await matrixDeterminant({ method: operation || 'cofactors', A });
                        localStorage.setItem('calc_last_result', JSON.stringify(res));
                        setLastResult(res);
                        window.dispatchEvent(new Event('calc:updated'));
                        setLoading(false);
                        return;
                      }

                      if (inputMode === 'reduce') {
                        // prepare Ab or A + b
                        const { A, errors: errA } = parseMatrix(matrixA);
                        const { out: b, errors: errb } = parseVector(vectorB);
                        if (Object.keys(errA).length) {
                          setMatrixErrorsA(errA);
                          setSubmitError('Hay entradas inválidas en la matriz A.');
                          setLoading(false);
                          return;
                        }
                        if (Object.keys(errb).length) {
                          setVectorErrorsB(errb);
                          setSubmitError('Hay entradas inválidas en el vector B.');
                          setLoading(false);
                          return;
                        }
                        const res = await matrixReduce({ method: operation === 'gauss_jordan' ? 'gauss-jordan' : 'gauss', A, b });
                        localStorage.setItem('calc_last_result', JSON.stringify(res));
                        setLastResult(res);
                        window.dispatchEvent(new Event('calc:updated'));
                        setLoading(false);
                        return;
                      }

                      if (inputMode === 'vector') {
                        // support linear combination which requires A and b
                        if (operation === 'linear_combination') {
                          const { A, errors: errA } = parseMatrix(matrixA);
                          const { out: b, errors: errb } = parseVector(vectorB);
                          if (Object.keys(errA).length) {
                            setMatrixErrorsA(errA);
                            setSubmitError('Hay entradas inválidas en la matriz A.');
                            setLoading(false);
                            return;
                          }
                          if (Object.keys(errb).length) {
                            setVectorErrorsB(errb);
                            setSubmitError('Hay entradas inválidas en el vector B.');
                            setLoading(false);
                            return;
                          }
                          const res = await vectorCombination({ A, b });
                          localStorage.setItem('calc_last_result', JSON.stringify(res));
                          setLastResult(res);
                          window.dispatchEvent(new Event('calc:updated'));
                          setLoading(false);
                          return;
                        }

                        // simple vector operations (add, subtract, dot)
                        const { out: u, errors: errU } = parseVector(vectorA);
                        const { out: v, errors: errV } = parseVector(vectorB);
                        if (Object.keys(errU).length) {
                          setVectorErrorsA(errU);
                          setSubmitError('Hay entradas inválidas en el vector A.');
                          setLoading(false);
                          return;
                        }
                        if (needsTwoInputs && Object.keys(errV).length) {
                          setVectorErrorsB(errV);
                          setSubmitError('Hay entradas inválidas en el vector B.');
                          setLoading(false);
                          return;
                        }

                        // build vectors mapping expected by backend
                        const vecs: Record<string, number[]> = {};
                        vecs['u'] = u;
                        if (needsTwoInputs) vecs['v'] = v;

                        const op = mapVectorOperation(operation);
                        if (!op) {
                          setSubmitError('Operación de vectores no soportada por el backend.');
                          setLoading(false);
                          return;
                        }

                        const res = await vectorOperate({ operation: op, vectors: vecs });
                        localStorage.setItem('calc_last_result', JSON.stringify(res));
                        setLastResult(res);
                        window.dispatchEvent(new Event('calc:updated'));
                        setLoading(false);
                        return;
                      }
                    } catch (e: any) {
                      console.error(e);
                      setSubmitError(e?.message || 'Error en la petición');
                      setLoading(false);
                    }
                  }}
                >
                  {loading ? 'Calculando...' : 'Calcular'}
                </Button>
              </div>
              <div className="backdrop-blur-lg bg-white/5 border border-white/10 rounded-xl p-6 min-h-32 flex items-center justify-center">
                <div className="w-full">
                  {submitError && <p className="text-red-400 mb-2">{submitError}</p>}
                  <p className="text-purple-300/50 text-center mb-3">
                    {selectedOperation ? `Operación seleccionada: ${selectedOperation.description}` : 'Selecciona una operación y presiona calcular'}
                  </p>

                  {/* Render lastResult if present */}
                  {lastResult ? (
                    <div className="text-left">
                      <ResultPretty result={lastResult} />
                    </div>
                  ) : (
                    <p className="text-purple-300/50 text-center">No hay resultados aún.</p>
                  )}
                </div>
              </div>
            </motion.div>
          </div>

          {/* Right Column - Keyboard */}
          <div className="lg:col-span-1">
              <DigitalKeyboard
                onKeyPress={handleKeyPress}
                // scalar has highest priority for keyboard input
                selectedCell={selectedScalar ? { scalar: true } : (selectedVectorCell ?? selectedMatrixCell)}
              />
          </div>
        </div>
      </div>
    </div>
  );
}
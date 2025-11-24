import { useState } from 'react';
import {  motion, AnimatePresence } from 'framer-motion';
import { Calculator, Keyboard, ChevronDown, ChevronUp, Delete, ChevronLeft, ChevronRight, ArrowLeft, ArrowRight, PercentSquare } from 'lucide-react';
import { Button } from '../ui/button';
import { MathExpressionEditor } from './MathExpressionEditor';

import { 
    insertAtCursor, 
    deleteAtCursor, 
    navigateLeft, 
    navigateRight,
    findNextEmptyField,
    findPreviousEmptyField 
}   from '../../utils/mathInputHelper';

type KeyboardCategory = 'basic' | 'functions' | 'trigonometry' | 'calculus';

interface MathKey {
    display: string;
    latex: string;
    description?: string;
}

const keyboardData: Record<KeyboardCategory, MathKey[]> = {
    basic: [
        { display: '7', latex: '7' },
        { display: '8', latex: '8' },
        { display: '9', latex: '9' },
        { display: '÷', latex: '\\div' },
        { display: '(', latex: '(' },
        { display: ')', latex: ')' },
        { display: '4', latex: '4' },
        { display: '5', latex: '5' },
        { display: '6', latex: '6' },
        { display: '×', latex: '\\times' },
        { display: '[', latex: '[' },
        { display: ']', latex: ']' },
        { display: '1', latex: '1' },
        { display: '2', latex: '2' },
        { display: '3', latex: '3' },
        { display: '−', latex: '-' },
        { display: '{', latex: '\\{' },
        { display: '}', latex: '\\}' },
        { display: '0', latex: '0' },
        { display: '.', latex: '.' },
        { display: '=', latex: '=' },
        { display: '+', latex: '+' },
        { display: ',', latex: ',' },
        { display: '∞', latex: '\\infty' },
    ],
    functions: [
        { display: 'xⁿ', latex: '^{n}', description: 'Potencia' },
        { display: 'x²', latex: '^{2}', description: 'Cuadrado' },
        { display: 'x³', latex: '^{3}', description: 'Cubo' },
        { display: 'x⁻¹', latex: '^{-1}', description: 'Inverso' },
        { display: 'ⁿ√x', latex: '\\sqrt[n]{}', description: 'Raíz n-ésima' },
        { display: '√x', latex: '\\sqrt{}', description: 'Raíz cuadrada' },
        { display: 'x/y', latex: '\\frac{}{}', description: 'Fracción' },
        { display: '|x|', latex: '\\left|\\right|', description: 'Valor absoluto' },
        { display: 'log', latex: '\\log', description: 'Logaritmo' },
        { display: 'ln', latex: '\\ln', description: 'Logaritmo natural' },
        { display: 'eˣ', latex: 'e^{}', description: 'Exponencial' },
        { display: '10ˣ', latex: '10^{}', description: 'Potencia de 10' },
        { display: 'π', latex: '\\pi', description: 'Pi' },
        { display: 'e', latex: 'e', description: 'Número e' },
        { display: '∑', latex: '\\sum_{}^{}', description: 'Sumatoria' },
        { display: '∏', latex: '\\prod_{}^{}', description: 'Productoria' },
        { display: 'x̄', latex: '\\bar{x}', description: 'Media' },
        { display: '±', latex: '\\pm', description: 'Más/menos' },
        { display: '≤', latex: '\\leq', description: 'Menor o igual' },
        { display: '≥', latex: '\\geq', description: 'Mayor o igual' },
        { display: '≠', latex: '\\neq', description: 'Diferente' },
        { display: '≈', latex: '\\approx', description: 'Aproximado' },
        { display: '∈', latex: '\\in', description: 'Pertenece' },
        { display: '∉', latex: '\\notin', description: 'No pertenece' },
    ],
    trigonometry: [
        { display: 'sin', latex: '\\sin', description: 'Seno' },
        { display: 'cos', latex: '\\cos', description: 'Coseno' },
        { display: 'tan', latex: '\\tan', description: 'Tangente' },
        { display: 'csc', latex: '\\csc', description: 'Cosecante' },
        { display: 'sec', latex: '\\sec', description: 'Secante' },
        { display: 'cot', latex: '\\cot', description: 'Cotangente' },
        { display: 'sin⁻¹', latex: '\\arcsin', description: 'Arcoseno' },
        { display: 'cos⁻¹', latex: '\\arccos', description: 'Arcocoseno' },
        { display: 'tan⁻¹', latex: '\\arctan', description: 'Arcotangente' },
        { display: 'sinh', latex: '\\sinh', description: 'Seno hiperbólico' },
        { display: 'cosh', latex: '\\cosh', description: 'Coseno hiperbólico' },
        { display: 'tanh', latex: '\\tanh', description: 'Tangente hiperbólica' },
        { display: 'θ', latex: '\\theta', description: 'Theta' },
        { display: 'α', latex: '\\alpha', description: 'Alpha' },
        { display: 'β', latex: '\\beta', description: 'Beta' },
        { display: 'γ', latex: '\\gamma', description: 'Gamma' },
        { display: 'φ', latex: '\\phi', description: 'Phi' },
        { display: 'λ', latex: '\\lambda', description: 'Lambda' },
        { display: 'μ', latex: '\\mu', description: 'Mu' },
        { display: 'σ', latex: '\\sigma', description: 'Sigma' },
        { display: 'ω', latex: '\\omega', description: 'Omega' },
        { display: '°', latex: '^\\circ', description: 'Grados' },
    ],
    calculus: [
        { display: 'd/dx', latex: '\\frac{d}{dx}', description: 'Derivada' },
        { display: 'd²/dx²', latex: '\\frac{d^2}{dx^2}', description: 'Segunda derivada' },
        { display: '∂/∂x', latex: '\\frac{\\partial}{\\partial x}', description: 'Derivada parcial' },
        { display: '∫', latex: '\\int', description: 'Integral' },
        { display: '∫ᵃᵇ', latex: '\\int_{}^{}', description: 'Integral definida' },
        { display: '∬', latex: '\\iint', description: 'Integral doble' },
        { display: '∭', latex: '\\iiint', description: 'Integral triple' },
        { display: '∮', latex: '\\oint', description: 'Integral de contorno' },
        { display: 'lim', latex: '\\lim_{}', description: 'Límite' },
        { display: 'lim→∞', latex: '\\lim_{n\\to\\infty}', description: 'Límite al infinito' },
        { display: 'Σⁿ', latex: '\\sum_{i=1}^{n}', description: 'Sumatoria indexada' },
        { display: '∇', latex: '\\nabla', description: 'Nabla/Gradiente' },
        { display: '∂', latex: '\\partial', description: 'Derivada parcial' },
        { display: 'dx', latex: 'dx', description: 'Diferencial' },
        { display: 'dy', latex: 'dy', description: 'Diferencial y' },
        { display: 'dt', latex: 'dt', description: 'Diferencial t' },
        { display: '→', latex: '\\to', description: 'Tiende a' },
        { display: '∞', latex: '\\infty', description: 'Infinito' },
        { display: 'ε', latex: '\\epsilon', description: 'Epsilon' },
        { display: 'δ', latex: '\\delta', description: 'Delta' },
        { display: 'Δ', latex: '\\Delta', description: 'Delta mayúscula' },
        { display: '∃', latex: '\\exists', description: 'Existe' },
        { display: '∀', latex: '\\forall', description: 'Para todo' },
    ],
};




const categoryName: Record<KeyboardCategory, string> = {
    basic: 'Básico',
    functions: 'Funciones',
    trigonometry: 'Trigonometria',
    calculus: 'Cálculo',
}

export function MathInputSection() {
    const [showKeyboard, setShowKeyboard] = useState(false);
    const [expression, setExpression] = useState('');
    const [cursorPosition, setCursorPosition] = useState(0);
    const [activeCategory, setActiveCategory] = useState<KeyboardCategory>('basic');

    const handleKeyboardInput = (value: string) => {
        if (value === 'CLEAR') {
            setExpression('');
            setCursorPosition(0);
        } else if (value === 'BACKSPACE') {
            const result = deleteAtCursor(expression, cursorPosition);
            setExpression(result.newExpression);
            setCursorPosition(result.newPosition);
        } else{
            const result = insertAtCursor(expression, cursorPosition, value);
            setExpression(result.newExpression);
            setCursorPosition(result.newPosition);

            if (value.includes('{}')) {
                const nextField = findNextEmptyField(result.newExpression, result.newPosition - value.length);
                if (nextField !== null) {
                    setCursorPosition(nextField);
                }
            }
        }
    };

    const handleNavigateLeft = () => {
        const newPositon = navigateLeft(expression, cursorPosition);
        setCursorPosition(newPositon);
    };

    const handleNavigateRight = () => {
        const newPosition = navigateRight(expression, cursorPosition);
        setCursorPosition(newPosition);
    };

    const handleJumpToPreviousField = () => {
        const prevField = findPreviousEmptyField(expression, cursorPosition);
        if (prevField !== null) {
            setCursorPosition(prevField);
        }
    };

    const handleJumpToNextField = () => {
        const nextField = findNextEmptyField(expression, cursorPosition);
        if (nextField !== null) {
            setCursorPosition(nextField);
        }
    };

    const handleKeyPress = (key: MathKey) => {
        handleKeyboardInput(key.latex);
    }

    return (
    <motion.div
      className="px-8 py-20"
      initial={{ opacity: 0, y: 40 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 1.1 }}
    >
      <div className="max-w-6xl mx-auto">
        {/* Section Header */}
        <div className="text-center mb-12">
          <motion.div
            className="inline-flex items-center gap-2 backdrop-blur-xl bg-white/5 border border-white/10 rounded-full px-4 py-2 mb-6"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.2 }}
          >
            <Keyboard className="text-purple-400" size={16} />
            <span className="text-sm text-gray-300">Teclado</span>
          </motion.div>
          <motion.h2
            className="text-4xl text-white mb-4"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3 }}
          >
            Escribe Ecuaciones{' '}
            <span className="bg-gradient-to-r from-purple-400 to-pink-400 bg-clip-text text-transparent">
              Complejas
            </span>
          </motion.h2>
          <motion.p
            className="text-lg text-gray-400 max-w-2xl mx-auto"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.4 }}
          >
            Teclado matemático profesional con soporte para funciones, trigonometría, 
            cálculo y más. Similar a Photomath pero integrado en tu navegador.
          </motion.p>
        </div>

        {/* Toggle Button */}
        <motion.div
          className="flex justify-center mb-8"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
        >
          <Button
            onClick={() => setShowKeyboard(!showKeyboard)}
            size="lg"
            className="group relative bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white border-0 px-10 py-6 text-lg shadow-lg shadow-purple-500/25 hover:shadow-xl hover:shadow-purple-500/30 transition-all"
          >
            <span className="flex items-center gap-3">
              <Calculator size={24} />
              {showKeyboard ? 'Ocultar' : 'Mostrar'} Teclado Matemático
              {showKeyboard ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
            </span>
          </Button>
        </motion.div>

        {/* Expandable Keyboard Section */}
        <AnimatePresence>
          {showKeyboard && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              transition={{ duration: 0.3 }}
              className="overflow-hidden"
            >
              <div className="backdrop-blur-2xl bg-gradient-to-br from-slate-900/95 via-blue-950/95 to-slate-900/95 border border-white/20 rounded-3xl p-8 shadow-2xl">
                {/* Math Display Area */}
                <div className="mb-8">
                  <MathExpressionEditor expression={expression} cursorPosition={cursorPosition} />
                  
                  {/* Navigation Controls */}
                  <div className="mt-4 grid grid-cols-2 gap-3">
                    {/* Character Navigation */}
                    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-3">
                      <div className="text-xs text-gray-500 mb-2 text-center">Navegar Carácter</div>
                      <div className="flex gap-2">
                        <Button
                          onClick={handleNavigateLeft}
                          className="flex-1 backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white"
                          size="sm"
                        >
                          <ChevronLeft size={18} className="mr-1" />
                          Izq
                        </Button>
                        <Button
                          onClick={handleNavigateRight}
                          className="flex-1 backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white"
                          size="sm"
                        >
                          Der
                          <ChevronRight size={18} className="ml-1" />
                        </Button>
                      </div>
                    </div>

                    {/* Field Navigation */}
                    <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-3">
                      <div className="text-xs text-gray-500 mb-2 text-center">Saltar a Campo</div>
                      <div className="flex gap-2">
                        <Button
                          onClick={handleJumpToPreviousField}
                          className="flex-1 backdrop-blur-xl bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/30 text-purple-300"
                          size="sm"
                        >
                          <ArrowLeft size={18} className="mr-1" />
                          Ant
                        </Button>
                        <Button
                          onClick={handleJumpToNextField}
                          className="flex-1 backdrop-blur-xl bg-purple-500/20 hover:bg-purple-500/30 border border-purple-400/30 text-purple-300"
                          size="sm"
                        >
                          Sig
                          <ArrowRight size={18} className="ml-1" />
                        </Button>
                      </div>
                    </div>
                  </div>
                  
                  {/* Expression Preview (LaTeX) */}
                  <div className="mt-4 backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-4">
                    <div className="text-xs text-gray-500 mb-2">LaTeX:</div>
                    <div className="text-sm text-gray-300 font-mono break-all min-h-[24px]">
                      {expression || 'Presiona las teclas para empezar a escribir...'}
                    </div>
                  </div>
                </div>

                {/* Category Tabs */}
                <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                  {(Object.keys(categoryName) as KeyboardCategory[]).map((category) => (
                    <button
                      key={category}
                      onClick={() => setActiveCategory(category)}
                      className={`px-6 py-3 rounded-xl transition-all whitespace-nowrap ${
                        activeCategory === category
                          ? 'bg-gradient-to-r from-blue-600 to-purple-600 text-white shadow-lg'
                          : 'backdrop-blur-lg bg-white/5 text-gray-400 hover:bg-white/10 hover:text-white'
                      }`}
                    >
                      {categoryName[category]}
                    </button>
                  ))}
                </div>

                {/* Keyboard Grid */}
                <AnimatePresence mode="wait">
                  <motion.div
                    key={activeCategory}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -10 }}
                    transition={{ duration: 0.2 }}
                    className="grid grid-cols-6 gap-3 mb-6"
                  >
                    {keyboardData[activeCategory].map((key, index) => (
                      <motion.button
                        key={`${key.latex}-${index}`}
                        onClick={() => handleKeyPress(key)}
                        className="group relative backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl p-4 transition-all hover:scale-105 active:scale-95"
                        whileHover={{ y: -2 }}
                        title={key.description}
                      >
                        <div className="text-white text-lg">{key.display}</div>
                        {key.description && (
                          <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-3 py-1 bg-slate-900 text-white text-xs rounded-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap shadow-lg border border-white/20 z-10">
                            {key.description}
                          </div>
                        )}
                      </motion.button>
                    ))}
                  </motion.div>
                </AnimatePresence>

                {/* Footer Actions */}
                <div className="flex gap-3">
                  <Button
                    onClick={() => handleKeyboardInput('BACKSPACE')}
                    className="flex-1 backdrop-blur-xl bg-red-500/20 hover:bg-red-500/30 border border-red-400/30 text-red-300"
                  >
                    <Delete size={20} className="mr-2" />
                    Borrar
                  </Button>
                  <Button
                    onClick={() => handleKeyboardInput('CLEAR')}
                    className="flex-1 backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/10 text-white"
                  >
                    Limpiar Todo
                  </Button>
                </div>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Features Grid */}
        {!showKeyboard && (
          <motion.div
            className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12"
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6 }}
          >
            {[
              { label: 'Operaciones Básicas', emoji: '➕' },
              { label: 'Funciones', emoji: '𝑓(𝑥)' },
              { label: 'Trigonometría', emoji: 'sin θ' },
              { label: 'Cálculo', emoji: '∫' },
            ].map((feature, i) => (
              <div
                key={i}
                className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-xl p-4 text-center"
              >
                <div className="text-2xl mb-2">{feature.emoji}</div>
                <div className="text-sm text-gray-400">{feature.label}</div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}
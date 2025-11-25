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
    label: string;
    latex: string;
    category: KeyboardCategory;
}

const categoryName: Record<KeyboardCategory, string> = {
    basic: 'Básico',
    functions: 'Funciones',
    trigonometry: 'Trigonometria',
    calculus: 'Cálculo',
}

const mathKeys: MathKey[] = [
    // Basic Operations
    { label: '7', latex: '7', category: 'basic' },
    { label: '8', latex: '8', category: 'basic' },
    { label: '9', latex: '9', category: 'basic' },
    { label: '÷', latex: '\\div', category: 'basic' },
    { label: '×', latex: '\\times', category: 'basic' },
    { label: '4', latex: '4', category: 'basic' },
    { label: '5', latex: '5', category: 'basic' },
    { label: '6', latex: '6', category: 'basic' },
    { label: '+', latex: '+', category: 'basic' },
    { label: '−', latex: '-', category: 'basic' },
    { label: '1', latex: '1', category: 'basic' },
    { label: '2', latex: '2', category: 'basic' },
    { label: '3', latex: '3', category: 'basic' },
    { label: '=', latex: '=', category: 'basic' },
    { label: '(', latex: '(', category: 'basic' },
    { label: '0', latex: '0', category: 'basic' },
    { label: '.', latex: '.', category: 'basic' },
    { label: ',', latex: ',', category: 'basic' },
    { label: ')', latex: ')', category: 'basic' },
    { label: 'π', latex: '\\pi', category: 'basic' },

    // Functions
    { label: 'x²', latex: '^{2}', category: 'functions' },
    { label: 'xⁿ', latex: '^{}', category: 'functions' },
    { label: '√', latex: '\\sqrt{}', category: 'functions' },
    { label: 'ⁿ√', latex: '\\sqrt[]{}', category: 'functions' },
    { label: '|x|', latex: '\\left|\\right|', category: 'functions' },
    { label: 'log', latex: '\\log', category: 'functions' },
    { label: 'ln', latex: '\\ln', category: 'functions' },
    { label: 'e', latex: 'e', category: 'functions' },
    { label: 'eˣ', latex: 'e^{}', category: 'functions' },
    { label: '10ˣ', latex: '10^{}', category: 'functions' },
    { label: 'x⁻¹', latex: '^{-1}', category: 'functions' },
    { label: 'x/y', latex: '\\frac{}{}', category: 'functions' },
    { label: '∞', latex: '\\infty', category: 'functions' },
    { label: '±', latex: '\\pm', category: 'functions' },
    { label: '≤', latex: '\\leq', category: 'functions' },
    { label: '≥', latex: '\\geq', category: 'functions' },
    { label: '≠', latex: '\\neq', category: 'functions' },
    { label: '∑', latex: '\\sum_{}^{}', category: 'functions' },
    { label: '∏', latex: '\\prod_{}^{}', category: 'functions' },
    { label: '%', latex: '\\%', category: 'functions' },

    // Trigonometry
    { label: 'sin', latex: '\\sin', category: 'trigonometry' },
    { label: 'cos', latex: '\\cos', category: 'trigonometry' },
    { label: 'tan', latex: '\\tan', category: 'trigonometry' },
    { label: 'csc', latex: '\\csc', category: 'trigonometry' },
    { label: 'sec', latex: '\\sec', category: 'trigonometry' },
    { label: 'cot', latex: '\\cot', category: 'trigonometry' },
    { label: 'sin⁻¹', latex: '\\sin^{-1}', category: 'trigonometry' },
    { label: 'cos⁻¹', latex: '\\cos^{-1}', category: 'trigonometry' },
    { label: 'tan⁻¹', latex: '\\tan^{-1}', category: 'trigonometry' },
    { label: 'sinh', latex: '\\sinh', category: 'trigonometry' },
    { label: 'cosh', latex: '\\cosh', category: 'trigonometry' },
    { label: 'tanh', latex: '\\tanh', category: 'trigonometry' },
    { label: 'θ', latex: '\\theta', category: 'trigonometry' },
    { label: 'α', latex: '\\alpha', category: 'trigonometry' },
    { label: 'β', latex: '\\beta', category: 'trigonometry' },
    { label: 'γ', latex: '\\gamma', category: 'trigonometry' },
    { label: 'δ', latex: '\\delta', category: 'trigonometry' },
    { label: 'ω', latex: '\\omega', category: 'trigonometry' },
    { label: 'φ', latex: '\\phi', category: 'trigonometry' },
    { label: '°', latex: '^\\circ', category: 'trigonometry' },

    // Calculus
    { label: 'd/dx', latex: '\\frac{d}{dx}', category: 'calculus' },
    { label: '∫', latex: '\\int', category: 'calculus' },
    { label: '∫ₐᵇ', latex: '\\int_{}^{}', category: 'calculus' },
    { label: '∂', latex: '\\partial', category: 'calculus' },
    { label: 'lim', latex: '\\lim_{}', category: 'calculus' },
    { label: 'lim→∞', latex: '\\lim_{n\\to\\infty}', category: 'calculus' },
    { label: 'Σ', latex: '\\sum', category: 'calculus' },
    { label: '∇', latex: '\\nabla', category: 'calculus' },
    { label: '∆', latex: '\\Delta', category: 'calculus' },
    { label: '→', latex: '\\to', category: 'calculus' },
    { label: '∈', latex: '\\in', category: 'calculus' },
    { label: '∀', latex: '\\forall', category: 'calculus' },
    { label: '∃', latex: '\\exists', category: 'calculus' },
    { label: 'ℝ', latex: '\\mathbb{R}', category: 'calculus' },
    { label: 'ℕ', latex: '\\mathbb{N}', category: 'calculus' },
    { label: 'ℤ', latex: '\\mathbb{Z}', category: 'calculus' },
    { label: 'ℚ', latex: '\\mathbb{Q}', category: 'calculus' },
    { label: 'ℂ', latex: '\\mathbb{C}', category: 'calculus' },
    { label: '∅', latex: '\\emptyset', category: 'calculus' },
    { label: '∪', latex: '\\cup', category: 'calculus' },
]


export function MathInputSection() {
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
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 1.5 }}
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
                {mathKeys.filter(key => key.category === activeCategory).map((key, index) => (
                  <motion.button
                    key={`${key.latex}-${index}`}
                    onClick={() => handleKeyPress(key)}
                    className="group relative backdrop-blur-xl bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-xl p-4 transition-all hover:scale-105 active:scale-95"
                    whileHover={{ y: -2 }}
                  >
                    <div className="text-white text-lg">{key.label}</div>
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
      </div>
    </motion.div>
  );
}
import React from 'react';
import { motion } from 'framer-motion';
import { ArrowLeft, Calculator as CalcIcon, Triangle } from 'lucide-react';
import { Button } from './ui/button';
import { DigitalKeyboard } from './DigitalKeyboard';
import { ErrorAcumuladoInputs } from './inputs/ErrorAcumuladoInputs';
import { ErrorAbsRelInputs } from './inputs/ErrorAbsRelInputs';
import { Tabs, TabsList, TabsTrigger } from './ui/tabs';

interface NumericMethodsProps {
  onBack?: () => void;
}

export function NumericMethods({ onBack }: NumericMethodsProps) {
  const [selectedOp, setSelectedOp] = React.useState<'acumulado' | 'absoluto_relativo'>('acumulado');
  return (
    <div className="min-h-screen relative overflow-hidden p-4 md:p-8">
      <div className="absolute inset-0 opacity-5" style={{
        backgroundImage: `linear-gradient(rgba(99, 102, 241, 0.4) 1px, transparent 1px),
                          linear-gradient(90deg, rgba(99, 102, 241, 0.4) 1px, transparent 1px)`,
        backgroundSize: '40px 40px',
      }} />

      <motion.div className="relative z-10 mb-6" initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-4 flex items-center justify-between">
          <Button onClick={onBack} variant="ghost" className="text-blue-200 hover:text-blue-100 hover:bg-white/10">
            <ArrowLeft className="mr-2" size={20} />
            Volver
          </Button>
          <div className="flex items-center gap-3">
            <CalcIcon className="text-purple-300" size={24} />
            <h2 className="text-2xl bg-gradient-to-r from-blue-300 to-purple-300 bg-clip-text text-transparent">Métodos Numéricos</h2>
          </div>
          <div className="w-24" />
        </div>
      </motion.div>

      <div className="relative z-10 max-w-7xl mx-auto">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-2 space-y-6">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }} className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-6">
              <div className="text-sm font-semibold text-blue-200 mb-4">Calculadora de Métodos Numéricos</div>

              <div className="mb-4">
                <Tabs value={selectedOp} onValueChange={(v) => setSelectedOp(v as 'acumulado' | 'absoluto_relativo')} className="w-full">
                  <TabsList className="grid w-full mx-auto grid-cols-2 backdrop-blur-xl bg-white/5 border border-white/10 h-12 text-white">
                    <TabsTrigger value="acumulado" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-blue-600 data-[state=active]:to-purple-600 text-base">
                      <CalcIcon className="w-4 h-4 mr-2" />
                      Error Acumulado
                    </TabsTrigger>

                    <TabsTrigger value="absoluto_relativo" className="data-[state=active]:bg-gradient-to-r data-[state=active]:from-purple-600 data-[state=active]:to-pink-600 text-base">
                      <Triangle className="w-4 h-4 mr-2" />
                      Error Absoluto y Relativo
                    </TabsTrigger>
                  </TabsList>
                </Tabs>
              </div>

              {/* Render selected operation inputs */}
              <div className="mt-4">
                {selectedOp === 'acumulado' && (
                  <ErrorAcumuladoInputs onCalculate={(data) => { console.log('Error Acumulado', data); }} />
                )}

                {selectedOp === 'absoluto_relativo' && (
                  <ErrorAbsRelInputs onCalculate={(data) => { console.log('Error Abs/Rel', data); }} />
                )}
              </div>

              
            </motion.div>
          </div>

          {/* Right column: keyboard placeholder */}
          <div className="lg:col-span-1">
            <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-4">
              <div className="text-sm font-semibold text-blue-200 mb-3">Teclado</div>
              <DigitalKeyboard onKeyPress={() => { /* placeholder: keyboard will be wired to inputs later */ }} selectedCell={null} />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default NumericMethods;

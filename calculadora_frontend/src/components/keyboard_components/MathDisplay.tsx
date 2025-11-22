import { useEffect, useRef } from "react";
import katex from "katex";

interface MathDisplayProps {
    expression: string;
}

export function MathDisplay({ expression }: MathDisplayProps) {
    const displayRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (displayRef.current && expression){
            try {
                katex.render(expression, displayRef.current, {
                    throwOnError: false,
                    displayMode: true,
                });
            } catch (error){
                if (displayRef.current) {
                    displayRef.current.textContent = expression;
                }
            }
        } else if (displayRef.current && !expression) {
            displayRef.current.textContent = '';
        }
    }, [expression]);

    return (
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
            <div className="text-sm text-gray-400 mb-3">Expresión</div>
            <div 
                ref={displayRef}
                className="text-white text-2xl min-h-[60px] flex items-center justify-center"
            />
        </div>
    );
}
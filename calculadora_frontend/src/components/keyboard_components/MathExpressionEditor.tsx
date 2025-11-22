import {  useEffect, useRef} from "react";
import katex from "katex";

interface MathExpressionEditorProps {
    expression: string;
    cursorPosition: number;
    onCursorClick?: (position: number) => void;
}

export function MathExpressionEditor({ expression, cursorPosition, onCursorClick }: MathExpressionEditorProps) {
    const containerRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (containerRef.current) {
            containerRef.current.innerHTML = '<span class="text-gray-500 text-xl">Presiona las teclas para comenzar...</span>';
            return;
        }

        try {
            let processedExpression = expression;
            let cursorInserted = false;

            const emptyFieldPositions: number[] = [];
            for (let i = 0; i <= expression.length - 1; i++) {
                if (expression[i] === '{' && expression[i + 1] === '}'){
                    emptyFieldPositions.push(i+1);
                }
            }

            let offset = 0;
            emptyFieldPositions.forEach((pos, index) => {
                const adjustedPos = pos + offset - 1;
                const isActive = cursorPosition === pos;

                const marker = isActive ? `{\\text{XACTIVEX${index}}}` : `{\\text{XEMPTYX${index}}}`;
                processedExpression = processedExpression.slice(offset, adjustedPos) + marker + processedExpression.slice(adjustedPos + 2);

                offset += marker.length -2;
                if (isActive){
                    cursorInserted = true;
                }
            });

            if (!cursorInserted) {
                const adjustedCursor = cursorPosition + (processedExpression.length - expression.length);
                processedExpression = processedExpression.slice(0, adjustedCursor) + `{\\text{XCURSORX}}` + processedExpression.slice(adjustedCursor);
            }

            const tempDiv = document.createElement('div');
            katex.render(processedExpression, tempDiv, {
                throwOnError: false,
                displayMode: true,
            });

            // Obtener HTML renderizado
            let renderedHTML = tempDiv.innerHTML;

            // Reemplazar marcadores con HTML personalizado
            // Campos activos
            renderedHTML = renderedHTML.replace(/XACTIVEX\d+/g, 
                '<span class="math-field-active-inline"><span class="math-cursor-inline">|</span></span>'
            );

            // Campos vacíos
            renderedHTML = renderedHTML.replace(/XEMPTYX\d+/g, 
                '<span class="math-field-empty-inline">&nbsp;</span>'
            );

            // Cursor solo
            renderedHTML = renderedHTML.replace(/XCURSORX/g, 
                '<span class="math-cursor-inline">|</span>'
            );

            containerRef.current.innerHTML = renderedHTML;
        } catch (error) {
            console.error('Error renmdering math:', error);
            if (containerRef.current) {
                containerRef.current.textContent = expression;
            }
        }
    }, [expression, cursorPosition]);

    return (
        <div className="backdrop-blur-xl bg-white/5 border border-white/10 rounded-2xl p-8">
            <div className="text-sm text-gray-400 mb-3">Expresión</div>
            <div 
                ref={containerRef}
                className="text-white text-2xl min-h-[80px] flex items-center justify-center cursor-text math-expression-container"
                style={{ 
                    userSelect: 'none',
                }}
                />
            <style>{`
                .math-cursor-inline) {
                    color: rgb(96, 165, 250);
                    animation: blink-float 1s ease-in-out infinite;
                    margin: 0 2px;
                    display: inline-block;
                    font-family: monospace;
                    font-size: 1.2em;
                }

                .math-field-empty-inline) {
                    border: 2px dashed rgba(156, 163, 175, 0.5);
                    border-radius: 4px;
                    padding: 2px 8px;
                    background: rgba(156, 163, 175, 0.1);
                    display: inline-block;
                    min-width: 20px;
                    min-height: 1em;
                }

                .math-field-active-inline) {
                    border: 2px dashed rgba(147, 51, 234, 0.8);
                    border-radius: 4px;
                    padding: 2px 8px;
                    background: rgba(147, 51, 234, 0.2);
                    display: inline-block;
                    min-width: 20px;
                    animation: pulse-field-inline 1.5s ease-in-out infinite;
                }

                @keyframes blink-float {
                    0%, 100% { 
                        opacity: 1;
                        transform: translateY(0px);
                    }
                    50% { 
                        opacity: 0.3;
                        transform: translateY(-2px);
                    }
                }

                @keyframes pulse-field-inline {
                    0%, 100% { 
                        border-color: rgba(147, 51, 234, 0.8);
                        background: rgba(147, 51, 234, 0.2);
                    }
                    50% { 
                        border-color: rgba(147, 51, 234, 1);
                        background: rgba(147, 51, 234, 0.3);
                    }
                }`
            }</style>
      </div>
    );
}
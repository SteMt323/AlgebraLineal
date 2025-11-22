export type SpecialOperation =
    | 'power' 
    | 'fraction' 
    | 'sqrt' 
    | 'nthRoot' 
    | 'abs' 
    | 'integral' 
    | 'integralBounds'
    | 'sum'
    | 'limit'
    | 'limitInfinity';

export const operationTemplates: Record<string, { latex: string; fields: number; description: string }> = {
    // Potencias
    '^{n}': { latex: '^{}', fields: 1, description: 'Potencia' },
    '^{2}': { latex: '^{2}', fields: 0, description: 'Cuadrado' },
    '^{3}': { latex: '^{3}', fields: 0, description: 'Cubo' },
    '^{-1}': { latex: '^{-1}', fields: 0, description: 'Inverso' },
    
    // Raíces
    '\\sqrt{}': { latex: '\\sqrt{}', fields: 1, description: 'Raíz cuadrada' },
    '\\sqrt[n]{}': { latex: '\\sqrt[]{}', fields: 2, description: 'Raíz n-ésima' },
    
    // Fracciones
    '\\frac{}{}': { latex: '\\frac{}{}', fields: 2, description: 'Fracción' },
    
    // Valor absoluto
    '\\left|\\right|': { latex: '\\left|\\right|', fields: 1, description: 'Valor absoluto' },
    
    // Exponenciales
    'e^{}': { latex: 'e^{}', fields: 1, description: 'Exponencial' },
    '10^{}': { latex: '10^{}', fields: 1, description: 'Potencia de 10' },
    
    // Sumatorias y productorias
    '\\sum_{}^{}': { latex: '\\sum_{}^{}', fields: 2, description: 'Sumatoria' },
    '\\prod_{}^{}': { latex: '\\prod_{}^{}', fields: 2, description: 'Productoria' },
    
    // Integrales
    '\\int': { latex: '\\int', fields: 0, description: 'Integral' },
    '\\int_{}^{}': { latex: '\\int_{}^{}', fields: 2, description: 'Integral definida' },
    
    // Límites
    '\\lim_{}': { latex: '\\lim_{}', fields: 1, description: 'Límite' },
    '\\lim_{n\\to\\infty}': { latex: '\\lim_{n\\to\\infty}', fields: 0, description: 'Límite al infinito' },
}

// Encontrar los campos vacios de las llaves en las expresiones ingresadas por el user

export function findEmptyFields(expression: string): number[] {
    const positions: number[] = [];
    const regex = /\{\}/g;
    let match;

    while ((match = regex.exec(expression)) !== null) {
        positions.push(match.index + 1); // +1 para obtener la posición dentro de las llaves        
    }

    return positions;
}

export function findNextEmptyField(expression: string, cursorPosition: number): number | null {
    const emptyFields = findEmptyFields(expression);

    for (const fieldPos of emptyFields) {
        if ( fieldPos > cursorPosition ) {
            return fieldPos;
        }
    }

    return emptyFields.length > 0 ? emptyFields[0] : null;
}

export function findPreviousEmptyField(expression: string, currentPostion: number): number | null {
    const emptyFields = findEmptyFields(expression);
    for (let i = emptyFields.length - 1; i >= 0; i--) {
        if ( emptyFields[i] < currentPostion ) {
            return emptyFields[i];
        }
    }

    return emptyFields.length > 0 ? emptyFields[emptyFields.length - 1] : null;
}

export function isInsideEmptyField(expression: string, position: number): boolean {
    if (position > 0 && position < expression.length) {
        const before = expression[position - 1];
        const after = expression[position];
        return before === '{' && after === '}';
    }
    return false;
}

export function navigationLeft(expression: string, currentPostion: number): number {
    if (currentPostion === 0) return 0;

    if (isInsideEmptyField(expression, currentPostion)) {
        return currentPostion - 1;
    }

    if (expression[currentPostion - 1] === '}') {
        let braceCount = 1;
        let pos = currentPostion - 2;
        while (pos >= 0 && braceCount > 0) {
            if (expression[pos] === '}') braceCount++;
            if (expression[pos] === '{') braceCount--;
            if (braceCount > 0) pos--;
        }

        return pos
    }
    if (expression[currentPostion - 1] === '{' && expression[currentPostion] === '}') {
        return currentPostion - 1;
    }

    return currentPostion - 1;
}

export function navigateRight(expression: string, currentPostion: number): number {
    if (currentPostion >= expression.length) return expression.length;

    if (isInsideEmptyField(expression, currentPostion)) {
        return currentPostion + 1;
    }

    if (expression[currentPostion] === '{') {
        let braceCount = 1;
        let pos = currentPostion + 1;
        while (pos < expression.length && braceCount > 0) {
            if (expression[pos] === '{') braceCount++;
            if (expression[pos] === '}') braceCount--;
            if (braceCount > 0) pos++;
        }
        return pos + 1;
    } 
    return currentPostion + 1;
}

export function insertAtCursor(expression: string, cursorPosition: number, text: string):{ newExpression: string; newCursorPosition: number } {
    if (isInsideEmptyField(expression, cursorPosition)) {
        const newExpression = expression.slice(0, cursorPosition - 1) + '{' + text + '}' + expression.slice(cursorPosition + 1);
        return {
            newExpression,
            newCursorPosition: cursorPosition + text.length,
        };
    }

    const newExpression = expression.slice (0, cursorPosition) + text + expression.slice(cursorPosition);
    return {
        newExpression,
        newCursorPosition: cursorPosition + text.length,
    }
}

export function deleteAtCursor(expression: string, cursorPosition: number): { newExpression: string; newPosition: number } {
    if (cursorPosition === 0) return { newExpression: expression, newPosition: 0 };
  
    // Si estamos en un campo vacío, borrar el campo completo y sus llaves
    if (isInsideEmptyField(expression, cursorPosition)) {
        const newExpression = 
            expression.slice(0, cursorPosition - 1) + 
            expression.slice(cursorPosition + 1);
        return {
            newExpression,
            newPosition: cursorPosition - 1,
        };
    }

    // Si borramos un }, verificar si quedará un campo vacío
    if (expression[cursorPosition - 1] === '}') {
        // Buscar el { correspondiente
        let braceCount = 1;
        let pos = cursorPosition - 2;

        while (pos >= 0 && braceCount > 0) {
            if (expression[pos] === '}') braceCount++;
            if (expression[pos] === '{') braceCount--;
            pos--;
        }

        pos++; // Ajustar a la posición del {

        // Verificar si entre { y } solo hay un carácter o está vacío
        const content = expression.slice(pos + 1, cursorPosition - 1);
        if (content.length <= 1) {
            // Borrar el contenido pero mantener {}
            const newExpression = 
            expression.slice(0, pos + 1) + 
            expression.slice(cursorPosition - 1);
            return {
            newExpression,
            newPosition: pos + 1,
            };
        }
    }

    // Borrado normal
    const newExpression = 
        expression.slice(0, cursorPosition - 1) + 
        expression.slice(cursorPosition);

    return {
        newExpression,
        newPosition: cursorPosition - 1,
    };
}
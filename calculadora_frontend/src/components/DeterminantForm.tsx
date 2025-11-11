import React, { useState } from 'react'
import { matrixDeterminant } from '../api/client'

export default function DeterminantForm() {
  const [A, setA] = useState('')
  const [method, setMethod] = useState('cofactors')
  const [loading, setLoading] = useState(false)

  function parseMatrix(text: string) {
    try {
      return JSON.parse(text)
    } catch (e) {
      return null
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const a = parseMatrix(A)
    if (!a) return alert('Matriz A inválida. Usa JSON como [[1,2],[3,4]]')
    setLoading(true)
    try {
      const res = await matrixDeterminant({ method, A: a })
      localStorage.setItem('calc_last_result', JSON.stringify(res))
      window.dispatchEvent(new Event('calc:updated'))
    } catch (err) {
      console.error(err)
      alert('Error al llamar la API. Revisa la consola.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <form className="det-form" onSubmit={onSubmit}>
      <h2>Determinante</h2>

      <label>
        Método
        <select value={method} onChange={(e) => setMethod(e.target.value)}>
          <option value="sarrus">Sarrus</option>
          <option value="cofactors">Cofactores</option>
          <option value="cramer">Cramer</option>
        </select>
      </label>

      <label>
        Matriz A (JSON)
        <textarea value={A} onChange={(e) => setA(e.target.value)} placeholder="Ej: [[1,2,3],[4,5,6],[7,8,9]]" />
      </label>

      <button type="submit" disabled={loading}>{loading ? 'Procesando...' : 'Calcular determinante'}</button>
    </form>
  )
}

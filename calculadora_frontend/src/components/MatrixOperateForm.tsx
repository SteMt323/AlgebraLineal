import React, { useState } from 'react'
import { matrixOperate } from '../api/client'

export default function MatrixOperateForm() {
  const [A, setA] = useState('')
  const [B, setB] = useState('')
  const [scalar, setScalar] = useState('')
  const [operation, setOperation] = useState('add')
  const [loading, setLoading] = useState(false)

  function parseMatrix(text: string) {
    try {
      // Expect JSON array like [[1,2],[3,4]]
      return JSON.parse(text)
    } catch (e) {
      return null
    }
  }

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    const payload: any = { operation }
    const a = parseMatrix(A)
    if (a) payload.A = a
    const b = parseMatrix(B)
    if (b) payload.B = b
    if (scalar) payload.scalar = Number(scalar)

    setLoading(true)
    try {
      const res = await matrixOperate(payload)
      // store result in localStorage so ResultViewer can pick it up (simple approach)
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
    <form className="matrix-form" onSubmit={onSubmit}>
      <h2>Operaciones de matriz</h2>
      <label>
        Operación
        <select value={operation} onChange={(e) => setOperation(e.target.value)}>
          <option value="add">Suma</option>
          <option value="sub">Resta</option>
          <option value="scalar">Escalar</option>
          <option value="transpose">Traspuesta</option>
          <option value="matmul">Multiplicar</option>
          <option value="inverse">Inversa</option>
        </select>
      </label>

      <label>
        Matriz A (JSON)
        <textarea value={A} onChange={(e) => setA(e.target.value)} placeholder="Ej: [[1,2],[3,4]]" />
      </label>

      <label>
        Matriz B (JSON) - opcional
        <textarea value={B} onChange={(e) => setB(e.target.value)} placeholder="Ej: [[5,6],[7,8]]" />
      </label>

      <label>
        Escalar (para operación escalar)
        <input value={scalar} onChange={(e) => setScalar(e.target.value)} />
      </label>

      <button type="submit" disabled={loading}>{loading ? 'Procesando...' : 'Calcular'}</button>
    </form>
  )
}

import axios from 'axios'

const API_BASE = (import.meta.env.VITE_API_BASE as string) || 'http://localhost:8000'

const client = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 15000,
})

export type MatrixPayload = {
  operation?: string
  A?: number[][]
  B?: number[][]
  scalar?: number
  matrices?: number[][][]
}

export async function matrixOperate(payload: MatrixPayload) {
  const res = await client.post('api/v1/matrix/operate', payload)
  return res.data
}

export async function matrixDeterminant(payload: { method: string; A: number[][] }) {
  const res = await client.post('api/v1/matrix/determinant', payload)
  return res.data
}

export async function matrixReduce(payload: { method: string; A?: number[][]; b?: number[]; Ab?: number[][]; options?: any }) {
  const res = await client.post('api/v1/matrix/reduce', payload)
  return res.data
}

export async function vectorOperate(payload: { operation: string; vectors: Record<string, number[]>; scalars?: Record<string, number>; options?: any }) {
  const res = await client.post('api/v1/vectors/operate', payload)
  return res.data
}

export async function vectorCombination(payload: { A: number[][]; b: number[]; options?: any }) {
  const res = await client.post('api/v1/vectors/combination', payload)
  return res.data
}

export default client

import React from 'react'
import './App.css'
import MatrixOperateForm from './components/MatrixOperateForm'
import DeterminantForm from './components/DeterminantForm'
import ResultViewer from './components/ResultViewer'

export default function App() {
  return (
    <div className="app-container">
      <h1>Calculadora Álgebra (Frontend - TypeScript)</h1>
      <div className="forms">
        <MatrixOperateForm />
        <DeterminantForm />
      </div>
      <ResultViewer />
    </div>
  )
}

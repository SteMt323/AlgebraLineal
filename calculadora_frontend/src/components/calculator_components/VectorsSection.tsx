import React from 'react';
import { VectorInput } from '../inputs/VectorInput';

type Props = {
  vectorA: any;
  vectorB: any;
  dimensionVectorA: number;
  dimensionVectorB: number;
  selectedVectorCell: any;
  setSelectedVectorCell: (v:any)=>void;
  setSelectedMatrixCell: (v:any)=>void;
  setSelectedScalar: (v:boolean)=>void;
  handleVectorCellChange: (name:'A'|'B', idx:number, v:string)=>void;
  vectorErrorsA: Record<string,string>;
  vectorErrorsB: Record<string,string>;
  onDimensionVectorAChange: (d:number)=>void;
  onDimensionVectorBChange: (d:number)=>void;
  needsTwoInputs: boolean;
};

export default function VectorsSection(props: Props) {
  const { vectorA, vectorB, dimensionVectorA, dimensionVectorB, selectedVectorCell, setSelectedVectorCell, setSelectedMatrixCell, setSelectedScalar, handleVectorCellChange, vectorErrorsA, vectorErrorsB, onDimensionVectorAChange, onDimensionVectorBChange, needsTwoInputs } = props;

  return (
    <>
      <VectorInput
        label="Vector A"
        vector={vectorA}
        dimension={dimensionVectorA}
        isSelected={selectedVectorCell?.vector === 'A'}
        selectedIndex={selectedVectorCell?.vector === 'A' ? selectedVectorCell.index : null}
        onSelectVector={() => {}}
        onSelectCell={(index) => {
          setSelectedVectorCell({ vector: 'A', index });
          setSelectedMatrixCell(null);
        }}
        onCellChange={(idx, v) => handleVectorCellChange('A', idx, v)}
        errors={vectorErrorsA}
        onDimensionChange={(dim) => onDimensionVectorAChange(dim)}
      />

      {needsTwoInputs && (
        <VectorInput
          label="Vector B"
          vector={vectorB}
          dimension={dimensionVectorB}
          isSelected={selectedVectorCell?.vector === 'B'}
          selectedIndex={selectedVectorCell?.vector === 'B' ? selectedVectorCell.index : null}
          onSelectVector={() => {}}
          onSelectCell={(index) => {
            setSelectedVectorCell({ vector: 'A', index });
            setSelectedMatrixCell(null);
            setSelectedScalar(false);
          }}
          onCellChange={(idx, v) => handleVectorCellChange('B', idx, v)}
          errors={vectorErrorsB}
          onDimensionChange={(dim) => onDimensionVectorBChange(dim)}
        />
      )}
    </>
  );
}

'use client'
import type { FC } from 'react'
import React, { useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import cn from 'classnames'
import VarReferencePicker from '../../_base/components/variable/var-reference-picker'
import { isComparisonOperatorNeedTranslate } from '../utils'
import type { Condition } from '@/app/components/workflow/nodes/if-else/types'
import { ComparisonOperator, LogicalOperator } from '@/app/components/workflow/nodes/if-else/types'
import type { ValueSelector } from '@/app/components/workflow/types'
import { Trash03 } from '@/app/components/base/icons/src/vender/line/general'
import { RefreshCw05 } from '@/app/components/base/icons/src/vender/line/arrows'
import Selector from '@/app/components/workflow/nodes/_base/components/selector'
const i18nPrefix = 'workflow.nodes.ifElse'

const Line = (
  <svg xmlns="http://www.w3.org/2000/svg" width="163" height="2" viewBox="0 0 163 2" fill="none">
    <path d="M0 1H162.5" stroke="url(#paint0_linear_641_36452)" />
    <defs>
      <linearGradient id="paint0_linear_641_36452" x1="162.5" y1="9.99584" x2="6.6086e-06" y2="9.94317" gradientUnits="userSpaceOnUse">
        <stop stopColor="#F3F4F6" />
        <stop offset="1" stopColor="#F3F4F6" stopOpacity="0" />
      </linearGradient>
    </defs>
  </svg>
)

const getOperators = (type: string) => {
  switch (type) {
    case 'string':
      return [
        ComparisonOperator.contains,
        ComparisonOperator.notContains,
        ComparisonOperator.startWith,
        ComparisonOperator.endWith,
        ComparisonOperator.is,
        ComparisonOperator.isNot,
        ComparisonOperator.empty,
        ComparisonOperator.notEmpty,
      ]
    case 'number':
      return [
        ComparisonOperator.equal,
        ComparisonOperator.notEqual,
        ComparisonOperator.largerThan,
        ComparisonOperator.lessThan,
        ComparisonOperator.largerThanOrEqual,
        ComparisonOperator.lessThanOrEqual,
        ComparisonOperator.is,
        ComparisonOperator.isNot,
        ComparisonOperator.empty,
        ComparisonOperator.notEmpty,
      ]
    case 'array':
      return [
        ComparisonOperator.is,
        ComparisonOperator.isNot,
        ComparisonOperator.empty,
        ComparisonOperator.notEmpty,
      ]
    default:
      return []
  }
}

type ItemProps = {
  readonly: boolean
  payload: Condition
  onChange: (newItem: Condition) => void
  canRemove: boolean
  onRemove?: () => void
  isShowLogicalOperator?: boolean
  logicalOperator: LogicalOperator
  onLogicalOperatorToggle: () => void
}

const Item: FC<ItemProps> = ({
  readonly,
  payload,
  onChange,
  canRemove,
  onRemove = () => { },
  isShowLogicalOperator,
  logicalOperator,
  onLogicalOperatorToggle,
}) => {
  const { t } = useTranslation()
  const isValueReadOnly = [ComparisonOperator.empty, ComparisonOperator.notEmpty, ComparisonOperator.isNull, ComparisonOperator.isNotNull].includes(payload.comparison_operator)

  const handleVarReferenceChange = useCallback((value: ValueSelector) => {
    onChange({
      ...payload,
      variable_selector: value,
    })
    // TODO: handle value type change will effect the comparisonOperators
  }, [onChange, payload])

  const handleValueChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    onChange({
      ...payload,
      value: e.target.value,
    })
  }, [onChange, payload])

  const handleComparisonOperatorChange = useCallback((v: ComparisonOperator) => {
    onChange({
      ...payload,
      comparison_operator: v,
    })
  }, [onChange, payload])

  return (
    <div className='space-y-2'>
      {isShowLogicalOperator && (
        <div className='flex items-center select-none'>
          <div className='flex items-center '>
            {Line}
            <div
              className='shrink-0 mx-1 flex items-center h-[22px] pl-2 pr-1.5 border border-gray-200 rounded-lg bg-white shadow-xs space-x-0.5 text-primary-600 cursor-pointer'
              onClick={onLogicalOperatorToggle}
            >
              <div className='text-xs font-semibold uppercase'>{t(`${i18nPrefix}.${logicalOperator === LogicalOperator.and ? 'and' : 'or'}`)}</div>
              <RefreshCw05 className='w-3 h-3' />
            </div>
            <div className=' rotate-180'>
              {Line}
            </div>
          </div>
        </div>
      )
      }

      <div className='flex items-center space-x-1'>
        <VarReferencePicker
          readonly={readonly}
          isShowNodeName
          className='grow'
          value={payload.variable_selector}
          onChange={handleVarReferenceChange}
        />

        <Selector
          popupClassName='top-[34px]'
          itemClassName='capitalize'
          trigger={
            <div className='shrink-0 w-[100px] whitespace-nowrap flex items-center h-8 justify-between px-2.5 rounded-lg bg-gray-100 capitalize cursor-pointer'>
              <div className='text-[13px] font-normal text-gray-900'>{isComparisonOperatorNeedTranslate(payload.comparison_operator) ? t(`${i18nPrefix}.comparisonOperator.${payload.comparison_operator}`) : payload.comparison_operator}</div>
            </div>
          }
          readonly={readonly}
          value={payload.comparison_operator}
          options={getOperators('string').map((o) => {
            return {
              label: isComparisonOperatorNeedTranslate(o) ? t(`${i18nPrefix}.comparisonOperator.${o}`) : o,
              value: o,
            }
          })}
          onChange={handleComparisonOperatorChange}
        />

        <input
          readOnly={readonly || isValueReadOnly}
          value={!isValueReadOnly ? payload.value : ''}
          onChange={handleValueChange}
          placeholder={!isValueReadOnly ? t(`${i18nPrefix}.enterValue`)! : ''}
          className='w-[80px] h-8 leading-8 px-2.5  rounded-lg border-0 bg-gray-100  text-gray-900 text-[13px]  placeholder:text-gray-400 focus:outline-none focus:ring-1 focus:ring-inset focus:ring-gray-200'
          type='text'
        />

        <div
          className={cn(canRemove ? 'text-gray-500 bg-gray-100 hover:bg-gray-200  cursor-pointer' : 'bg-gray-25 text-gray-300', 'p-2 rounded-lg ')}
          onClick={canRemove ? onRemove : () => { }}
        >
          <Trash03 className='w-4 h-4 ' />
        </div>
      </div>
    </div >

  )
}
export default React.memo(Item)
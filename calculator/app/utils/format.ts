export const number = (n: number | null, digits = 0) =>
  n === null ? 'Не рассчитан' : n.toLocaleString('ru-RU', { maximumFractionDigits: digits })
export const money = (n: number | null) =>
  n === null ? 'Не рассчитан' : `${number(n / 1e6, 1)} млн ₽`

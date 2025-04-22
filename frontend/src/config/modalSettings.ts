/**
 * Стандартные настройки для модальных окон
 * Этот файл создан, чтобы избежать проблем с отображением Modal и Drawer компонентов Mantine
 */

import { ModalProps, DrawerProps } from '@mantine/core';

/**
 * Стандартные настройки для Modal
 */
export const defaultModalSettings: Partial<ModalProps> = {
  centered: true,      // Центрирование окна
  overlayProps: {      // Настройки оверлея
    blur: 3,           // Размытие заднего фона
    opacity: 0.7,      // Непрозрачность
  },
  closeOnClickOutside: true,  // Закрытие при клике вне модалки
  closeOnEscape: true,        // Закрытие по Esc
  trapFocus: true,            // Фокус внутри модалки
  lockScroll: true,           // Блокировка прокрутки страницы
  transitionProps: { duration: 200 }, // Длительность анимации открытия/закрытия
  withinPortal: true,         // Рендер в портале (решает проблемы с z-index)
};

/**
 * Стандартные настройки для формы в модальном окне
 */
export const formModalSettings: Partial<ModalProps> = {
  ...defaultModalSettings,
  size: 'lg',           // Размер модалки для форм
  padding: 'md',        // Отступы внутри
};

/**
 * Стандартные настройки для модалки подтверждения
 */
export const confirmModalSettings: Partial<ModalProps> = {
  ...defaultModalSettings,
  size: 'sm',           // Маленький размер для подтверждений
  padding: 'md',        // Отступы
  closeOnClickOutside: false, // Запрет закрытия кликом (чтобы избежать случайного закрытия)
};

/**
 * Стандартные настройки для боковой панели (Drawer)
 */
export const defaultDrawerSettings: Partial<DrawerProps> = {
  overlayProps: {      // Настройки оверлея
    blur: 3,           // Размытие заднего фона
    opacity: 0.7,      // Непрозрачность
  },
  closeOnClickOutside: true,  // Закрытие при клике вне
  closeOnEscape: true,        // Закрытие по Esc
  position: 'right',          // Позиция (справа)
  size: '40%',                // Размер по умолчанию
  trapFocus: true,            // Фокус внутри
  lockScroll: true,           // Блокировка прокрутки страницы
  transitionProps: { duration: 200 }, // Анимация
  withinPortal: true,         // Рендер в портале
  padding: 'md',              // Отступы
};

/**
 * ВАЖНО! CSS-настройки которые необходимы для корректной работы модалок:
 * 
 * 1. НЕ ДОБАВЛЯТЬ в body:
 *    - display: flex
 *    - place-items: center
 *    - или другие свойства, влияющие на позиционирование
 * 
 * 2. НЕ ИСПОЛЬЗОВАТЬ position: fixed на родительских элементах модалок
 * 
 * 3. Использовать z-index осторожно, Mantine модалки имеют z-index: 200
 */ 
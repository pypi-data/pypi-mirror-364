import streamlit as st
from streamlit_crepe import st_milkdown

st.title("🧪 Тест режимов Placeholder")

st.markdown("""
Тестируем различные режимы для placeholder в Milkdown Crepe.
Из документации известен только режим `'block'`, но попробуем другие возможные варианты.
""")

# Создаем тест с разными режимами
modes_to_test = [
    ('block', 'Блочный режим (из документации)'),
    ('inline', 'Инлайн режим (предположение)'),
    ('text', 'Текстовый режим (предположение)'),
    ('paragraph', 'Параграф режим (предположение)'),
    ('line', 'Строчный режим (предположение)'),
]

st.subheader("Тестирование режимов placeholder")

for mode, description in modes_to_test:
    with st.expander(f"Режим: {mode} - {description}"):
        st.markdown(f"**Режим:** `mode: '{mode}'`")
        
        try:
            # Создаем компонент с кастомным режимом
            # Поскольку мы не можем напрямую передать mode через API,
            # покажем как это должно выглядеть в коде
            st.code(f"""
// В CrepeEditor.tsx:
[Crepe.Feature.Placeholder]: {{
    text: 'Placeholder для режима {mode}',
    mode: '{mode}',
}},
            """, language="typescript")
            
            # Создаем обычный компонент для демонстрации
            content = st_milkdown(
                placeholder=f"Placeholder для режима {mode}",
                height=150,
                key=f"test_mode_{mode}"
            )
            
            if content:
                st.markdown("**Содержимое:**")
                st.code(content[:100] + "..." if len(content) > 100 else content)
                
        except Exception as e:
            st.error(f"Ошибка при тестировании режима {mode}: {e}")

st.subheader("📚 Информация из документации")

st.markdown("""
### Известные режимы из документации Milkdown:

**1. `mode: 'block'`** (подтвержден)
```typescript
[Crepe.Feature.Placeholder]: {
    text: 'Start writing...', 
    mode: 'block',
}
```

### Возможные режимы (требуют тестирования):

Основываясь на архитектуре ProseMirror и Milkdown, возможны следующие режимы:

- **`'inline'`** - Инлайн placeholder (внутри строки)
- **`'paragraph'`** - На уровне параграфа
- **`'document'`** - На уровне документа
- **`'node'`** - На уровне узла

### Как добавить поддержку других режимов:

Чтобы добавить поддержку других режимов в наш компонент, нужно:

1. **Добавить параметр в API:**
```python
def st_milkdown(
    placeholder: str = "",
    placeholder_mode: str = "block",  # Новый параметр
    # другие параметры...
):
```

2. **Обновить frontend:**
```typescript
[Crepe.Feature.Placeholder]: {
    text: args.placeholder || 'Start writing...',
    mode: args.placeholder_mode || 'block',
},
```

3. **Протестировать режимы:**
- Проверить какие режимы поддерживает Milkdown
- Убедиться что они работают корректно
- Добавить валидацию для поддерживаемых режимов
""")

st.subheader("🔬 Экспериментальное тестирование")

st.markdown("""
Для полного тестирования режимов placeholder нужно:

1. **Изучить исходный код Milkdown** - найти все поддерживаемые режимы
2. **Создать тестовую версию** компонента с параметром `placeholder_mode`
3. **Протестировать каждый режим** и документировать поведение
4. **Добавить валидацию** для корректных режимов

### Текущий статус:
- ✅ **`'block'`** - Подтвержден документацией
- ❓ **Другие режимы** - Требуют исследования исходного кода Milkdown
""")

# Показываем текущую реализацию
st.subheader("📝 Текущая реализация")

st.code("""
// Текущая конфигурация в CrepeEditor.tsx:
[Crepe.Feature.Placeholder]: {
    text: args.placeholder || 'Start writing...',
    mode: 'block', // Жестко задан режим 'block'
},
""", language="typescript")

st.markdown("""
**Вывод:** В данный момент поддерживается только режим `'block'`. 
Для добавления других режимов нужно исследовать документацию Milkdown 
и добавить соответствующий параметр в API компонента.
""")
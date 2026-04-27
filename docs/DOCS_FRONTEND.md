# Documentação Frontend - Mapa & UX

Este documento detalha o funcionamento da interface do Mapa, especificamente a lógica de ícones e customização visual.

## 🎨 Ícones Personalizados

A renderização dos ícones no mapa utiliza a função JavaScript `getIconForCategory(tipo)` (definida em `/app/templates/mapa/index.html`).

Em vez de usar imagens estáticas (`.png`), utilizamos **SVG Inline** gerado via código. Isso permite alterar a cor do ícone dinamicamente sem precisar de múltiplos arquivos de imagem.

### Cores Padrão
As cores são definidas no objeto `colors` dentro da função:
- **Cisterna**: Azul Escuro (`#003366`)
- **Barreiro**: Marrom/Laranja (`#D2691E`)
- **Beneficiário**: Verde (`#28a745`)
- **Calçadão**: Cinza (`#808080`)
- **Área de Roça**: Verde Claro (`#90EE90`)
- **Default**: Azul Padrão (`#3388ff`)

### Como adicionar ou alterar um ícone

#### Opção 1: Alterar Cor (Recomendado)
Para mudar a cor de uma categoria existente ou adicionar uma nova:
1. Abra `app/templates/mapa/index.html`.
2. Localize a função `getIconForCategory`.
3. Adicione ou edite a entrada no objeto `colors`:
```javascript
const colors = {
    'Nova Categoria': '#FF0000', // Vermelho
    ...
};
```

#### Opção 2: Usar Ícone de Imagem (Arquivo Static)
Se preferir usar um arquivo de imagem (ex: `meu_icone.png`):
1. Salve a imagem em `app/static/icons/meu_icone.png`.
2. Edite a função `getIconForCategory` para retornar um `L.icon` normal caso o tipo coincida:

```javascript
if (tipo === 'Minha Categoria Especial') {
    return L.icon({
        iconUrl: '/static/icons/meu_icone.png',
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -32]
    });
}
```

## 🖼️ Miniaturas nos Popups

O popup do mapa verifica automaticamente se o objeto do ponto possui uma propriedade `foto` ou `imagem`.
Se existir (e não for nula), uma miniatura de **100px** de largura é exibida logo abaixo do nome do ponto.

```javascript
// Lógica interna (não precisa editar a menos que mude o nome do campo)
const imgSrc = p.foto || p.imagem || null;
```

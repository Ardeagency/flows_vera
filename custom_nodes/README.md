# custom_nodes — ComfyUI dependencies para flows_vera

Snapshot de los custom nodes de ComfyUI que usan los flows de `papermate/` y `ignis/` (y futuros clientes de AI Smart Content).

## Propósito

Este directorio existe para que el servidor `content-flows` pueda reproducir el entorno completo de ComfyUI sin tener que clonar manualmente cada custom node desde su repo upstream.

## Instalación en content-flows

```bash
cd /path/to/ComfyUI
cp -r /path/to/flows_vera/custom_nodes/* ./custom_nodes/
# Instalar dependencias Python de cada node
find ./custom_nodes -name "requirements.txt" -exec pip install -r {} \;
# Reiniciar ComfyUI
```

## Custom nodes incluidos

Ver `MANIFEST.json` para la lista completa con URL upstream + commit hash al momento del snapshot.

### Nodo custom de ARDE
- **ComfyUI-Kie-API** — fork extendido del autor `gateway/` con nodos custom agregados por ARDE:
  - `KIE_NanoBananaPro_Image` (4K)
  - `KIE_Kling3_Video`
  - `KIE_Seedance2_Video`
  - `KIE_GPTImage2_T2I` y `KIE_GPTImage2_I2I` (agregados 2026-05-18, no existen upstream)

## Política de updates

Cuando un custom node upstream tenga update relevante:
1. Reclonar desde upstream
2. Reemplazar la carpeta en este directorio
3. Actualizar entrada en `MANIFEST.json` con nuevo commit hash
4. Commit con mensaje `chore(custom_nodes): update <NodeName> to <commit>`

## Modelos pesados

Los `.safetensors`, `.pth`, `.bin`, etc. NO están versionados (ver `.gitignore`). Se descargan en runtime cuando ComfyUI los pide o se copian manualmente al directorio `models/` de ComfyUI.

## Snapshot info
- Fecha snapshot: 2026-05-25
- Origen: `~/Documents/custom_nodes/` (Mac Studio M1 Max, ARDE)
- Total custom nodes: 18

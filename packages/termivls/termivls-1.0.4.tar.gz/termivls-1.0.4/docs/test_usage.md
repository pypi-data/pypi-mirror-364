# TermiVis 使用示例

现在您可以在Claude Code中使用以下命令来分析图片：

## 📸 可用的图片分析工具

### 1. 分析图片 (analyze_image)
```
请使用analyze_image工具分析这张图片：/path/to/your/image.jpg
分析提示："这张图片显示了什么内容？"
```

### 2. 详细描述图片 (describe_image)  
```
请使用describe_image工具详细描述这张图片：/path/to/your/image.jpg
详细级别：detailed
```

### 3. 提取图片中的文字 (extract_text)
```
请使用extract_text工具从这张图片中提取文字：/path/to/your/document.jpg
```

### 4. 对比图片 (compare_images)
```
请使用compare_images工具对比这两张图片：
图片1：/path/to/image1.jpg  
图片2：/path/to/image2.jpg
```

### 5. 识别物体 (identify_objects)
```
请使用identify_objects工具识别这张图片中的物体：/path/to/your/image.jpg
包含位置信息：true
```

## 💡 支持的输入格式

- **本地文件**: `/path/to/image.jpg`, `./image.png`
- **网络图片**: `https://example.com/image.jpg`  
- **剪贴板**: `clipboard` (如果系统支持)

## 🎯 使用技巧

1. **批量处理**: 一次最多可以处理5张图片
2. **自动压缩**: 大于5MB的图片会自动压缩优化
3. **多格式支持**: PNG, JPG, WEBP, GIF, BMP都支持
4. **流式输出**: 分析结果会实时显示

开始体验TermiVis的强大图片分析能力吧！
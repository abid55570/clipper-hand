import type { CaptionStyle } from '../../types';

interface Props {
  text: string;
  style: CaptionStyle;
}

export default function CaptionPreview({ text, style }: Props) {
  const words = text.split(' ');

  return (
    <div style={{
      background: '#000',
      borderRadius: '8px',
      padding: '40px 20px',
      display: 'flex',
      justifyContent: 'center',
      alignItems: style.position === 'top' ? 'flex-start' :
                   style.position === 'center' ? 'center' : 'flex-end',
      minHeight: '200px',
    }}>
      <div style={{
        fontFamily: style.font_family,
        fontSize: `${Math.min(style.font_size, 36)}px`,
        fontWeight: style.bold ? 700 : 400,
        color: style.primary_color,
        textShadow: `2px 2px 0 ${style.outline_color}, -2px -2px 0 ${style.outline_color}`,
        textAlign: 'center',
        maxWidth: '80%',
      }}>
        {words.map((word, i) => {
          const isHighlighted = style.highlight_words.some(
            (hw) => word.toLowerCase().replace(/[.,!?]/g, '') === hw.toLowerCase()
          );
          return (
            <span key={i} style={{
              color: isHighlighted ? style.highlight_color : style.primary_color,
              fontWeight: isHighlighted ? 700 : undefined,
            }}>
              {word}{' '}
            </span>
          );
        })}
      </div>
    </div>
  );
}

function VideoCards({ videos }) {
  if (!videos || videos.length === 0) return null;

  return (
    <div className="mt-3 pt-3 border-t border-(--color-border)">
      <p className="text-xs text-(--color-chalk-dim) mb-2">Watch how to do it</p>
      <div className="flex flex-wrap gap-3">
        {videos.map((v) => (
          <a
            key={v.video_id}
            href={`https://www.youtube.com/watch?v=${v.video_id}`}
            target="_blank"
            rel="noopener noreferrer"
            className="w-44 hover:opacity-80 transition-opacity"
          >
            <img src={v.thumbnail} alt={v.title} className="w-full rounded-md" />
            <p className="text-xs font-medium mt-1 capitalize">{v.exercise}</p>
            <p className="text-[11px] text-(--color-chalk-dim) line-clamp-2">
              {v.title}
            </p>
          </a>
        ))}
      </div>
    </div>
  );
}

export default VideoCards;
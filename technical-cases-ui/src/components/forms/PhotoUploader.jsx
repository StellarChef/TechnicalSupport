import { ImagePlus } from "lucide-react";
import { useEffect, useRef } from "react";

export default function PhotoUploader({ photos, setPhotos }) {
  const fileInputRef = useRef(null);

  useEffect(() => {
    return () => {
      photos.forEach((photo) => {
        if (photo.previewUrl) {
          URL.revokeObjectURL(photo.previewUrl);
        }
      });
    };
  }, [photos]);

  const createPhotoItem = (file) => ({
    id: crypto.randomUUID(),
    name: file.name,
    isMain: photos.length === 0,
    file,
    previewUrl: URL.createObjectURL(file),
  });

  const handleFiles = (fileList) => {
    if (!fileList?.length) return;

    const allowedFiles = Array.from(fileList).filter((file) =>
      file.type.startsWith("image/")
    );

    const remainingSlots = 3 - photos.length;
    const newFiles = allowedFiles.slice(0, remainingSlots).map(createPhotoItem);

    if (newFiles.length === 0) return;

    setPhotos((prev) => [...prev, ...newFiles]);
  };

  const openFileDialog = () => {
    fileInputRef.current?.click();
  };

  const handleRemovePhoto = (id) => {
    setPhotos((prev) => prev.filter((item) => item.id !== id));
  };

  const setMainPhoto = (id) => {
    setPhotos((prev) =>
      prev.map((item) => ({
        ...item,
        isMain: item.id === id,
      }))
    );
  };

  const handleDrop = (event) => {
    event.preventDefault();
    event.stopPropagation();
    handleFiles(event.dataTransfer.files);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
    event.stopPropagation();
  };

  return (
    <div>
      <span className="mb-1 block text-xs font-semibold text-appBlack">
        Zdjęcia uszkodzenia
      </span>

      <input
        ref={fileInputRef}
        type="file"
        accept="image/*"
        multiple
        className="hidden"
        onChange={(event) => handleFiles(event.target.files)}
      />

      <div
        className="rounded-app border-2 border-dashed border-neutralGray bg-backgroundLight p-6 text-center"
        onDrop={handleDrop}
        onDragOver={handleDragOver}
      >
        <ImagePlus className="mx-auto text-darkGray" size={32} />

        <p className="mt-2 text-sm font-semibold text-appBlack">
          Przeciągnij zdjęcia lub dodaj pliki
        </p>

        <p className="mt-1 text-xs text-darkGray">
          JPG, PNG, WEBP · maksymalnie 3 zdjęcia · {photos.length}/3
        </p>

        <button
          onClick={openFileDialog}
          type="button"
          className="mt-4 rounded-full bg-primaryDark px-5 py-2.5 text-sm font-semibold text-white disabled:opacity-40 hover:bg-primaryDark/90"
          disabled={photos.length >= 3}
        >
          + Dodaj zdjęcia z komputera
        </button>
      </div>

      {photos.length >= 3 && (
        <p className="mt-2 text-xs font-semibold text-appBlack">
          Osiągnięto limit 3 zdjęć.
        </p>
      )}

      {photos.length > 0 && (
        <div className="mt-4 grid grid-cols-3 gap-3">
          {photos.map((photo) => (
            <div
              key={photo.id}
              className={`rounded-2xl border-2 p-3 transition-all ${
                photo.isMain
                  ? "border-primaryDark bg-primaryDark/5"
                  : "border-neutralGray bg-white"
              }`}
            >
              <div className="mb-2 flex h-20 items-center justify-center overflow-hidden rounded-xl bg-backgroundLight">
                {photo.previewUrl ? (
                  <img
                    src={photo.previewUrl}
                    alt={photo.name}
                    className="h-full w-full object-cover"
                  />
                ) : (
                  <ImagePlus size={22} className="text-darkGray" />
                )}
              </div>

              <p className="text-xs font-semibold text-appBlack truncate">
                {photo.name}
              </p>

              <div className="mt-2 flex gap-1.5">
                <button
                  type="button"
                  onClick={() => setMainPhoto(photo.id)}
                  className="flex-1 text-xs font-semibold text-appBlack hover:text-primaryDark"
                >
                  {photo.isMain ? "✓ Główne" : "Ustaw"}
                </button>

                <button
                  type="button"
                  onClick={() => handleRemovePhoto(photo.id)}
                  className="flex-1 text-xs font-semibold text-darkGray hover:text-red-600"
                >
                  Usuń
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

import Card from "../shared/Card";

export default function CasePhotoPreview({ photos = [] }) {
  const mainPhoto = photos.find((photo) => photo.isMain) || photos[0];

  return (
    <Card title="Zdjęcia">
      <div className="overflow-hidden rounded-app bg-neutralGray/20">
        {mainPhoto ? (
          <img
            src={mainPhoto.url}
            alt="Zdjęcie główne zgłoszenia"
            className="h-72 w-full object-cover"
          />
        ) : (
          <div className="flex h-72 items-center justify-center text-darkGray">
            Brak zdjęć
          </div>
        )}
      </div>

      <div className="mt-3 flex gap-3">
        {photos.map((photo) => (
          <div
            key={photo.id}
            className="relative h-20 w-20 overflow-hidden rounded-2xl border border-neutralGray"
          >
            <img
              src={photo.url}
              alt="Miniatura zgłoszenia"
              className="h-full w-full object-cover"
            />

            {photo.isMain && (
              <span className="absolute bottom-1 left-1 rounded-full bg-primaryDark px-2 py-0.5 text-[10px] text-white">
                główne
              </span>
            )}
          </div>
        ))}
      </div>
    </Card>
  );
}
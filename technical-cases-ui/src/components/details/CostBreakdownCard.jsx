import Card from "../shared/Card";
//import Cost from "../shared/cost";

export default function CostBreakdownCard({ cost }) {
  return (
    <Card title="Koszt naprawy">
      <div className="space-y-3 text-sm">
        <div className="flex justify-between">
          <span className="text-darkGray">Robocizna</span>
          <strong className="text-appBlack">
            {cost.labor} {cost.currency}
          </strong>
        </div>

        <div className="flex justify-between">
          <span className="text-darkGray">Materiał</span>
          <strong className="text-appBlack">
            {cost.materials} {cost.currency}
          </strong>
        </div>

        <div className="border-t border-neutralGray/40 pt-3">
          <div className="flex justify-between text-base">
            <span className="font-bold text-appBlack">Suma</span>
            <strong className="text-appBlack">
              {cost.total} {cost.currency}
            </strong>
          </div>
        </div>
      </div>
    </Card>
  );
}




import { AlertTriangle, CheckCircle, Clock } from 'lucide-react';
import { Tank } from '../../types/dashboard';
import { formatNumber } from '../../utils/formatters';
import { useIsMobile } from '../../hooks/useMobile';

interface SimpleTankStatusProps {
  tanks: Tank[];
}

export const SimpleTankStatus = ({ tanks }: SimpleTankStatusProps) => {
  const isMobile = useIsMobile();

  const getStatusInfo = (tank: Tank) => {
    switch (tank.washAlertStatus) {
      case 'critical':
        return {
          label: 'Needs Wash NOW',
          icon: AlertTriangle,
          bgColor: 'bg-red-50 border-red-200',
          textColor: 'text-red-700',
          iconColor: 'text-red-500',
          action: 'Call for pickup immediately'
        };
      case 'warning':
        return {
          label: 'Wash Soon',
          icon: Clock,
          bgColor: 'bg-orange-50 border-orange-200',
          textColor: 'text-orange-700',
          iconColor: 'text-orange-500',
          action: 'Schedule wash within 24 hours'
        };
      default:
        return {
          label: 'Tank OK',
          icon: CheckCircle,
          bgColor: 'bg-green-50 border-green-200',
          textColor: 'text-green-700',
          iconColor: 'text-green-500',
          action: 'No action needed'
        };
    }
  };

  // Group tanks by barn for easier understanding
  const tanksByBarn = tanks.reduce((acc, tank) => {
    const barnMatch = tank.name.match(/Barn (\d+)/);
    const barnNum = barnMatch ? parseInt(barnMatch[1]) : 1;
    if (!acc[barnNum]) acc[barnNum] = [];
    acc[barnNum].push(tank);
    return acc;
  }, {} as Record<number, Tank[]>);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className={`${isMobile ? 'text-lg' : 'text-xl'} font-bold text-slate-800`}>
          Tank Status
        </h3>
        <div className="text-sm text-slate-600">
          {tanks.length} tanks total
        </div>
      </div>

      {Object.entries(tanksByBarn).map(([barnNum, barnTanks]) => (
        <div key={barnNum} className="space-y-2">
          <h4 className={`${isMobile ? 'text-base' : 'text-lg'} font-semibold text-slate-700 border-b border-slate-200 pb-1`}>
            Barn {barnNum}
          </h4>
          
          <div className={`grid ${isMobile ? 'grid-cols-1' : 'grid-cols-2'} gap-3`}>
            {barnTanks.map((tank) => {
              const status = getStatusInfo(tank);
              const StatusIcon = status.icon;
              const fillPercentage = (tank.currentVolume / tank.capacity) * 100;
              
              return (
                <div
                  key={tank.id}
                  className={`${status.bgColor} border-2 rounded-lg ${isMobile ? 'p-3' : 'p-4'} transition-all hover:shadow-md`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <StatusIcon className={`${isMobile ? 'h-4 w-4' : 'h-5 w-5'} ${status.iconColor}`} />
                      <div>
                        <h5 className={`${isMobile ? 'text-sm' : 'text-base'} font-semibold ${status.textColor}`}>
                          {tank.name.replace('Barn ' + barnNum + ' - ', '')}
                        </h5>
                        <p className={`${isMobile ? 'text-xs' : 'text-sm'} font-medium ${status.textColor}`}>
                          {status.label}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-2">
                    <div className="flex justify-between items-center">
                      <span className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600`}>
                        Volume:
                      </span>
                      <span className={`${isMobile ? 'text-sm' : 'text-base'} font-semibold text-slate-800`}>
                        {formatNumber(tank.currentVolume)}L
                      </span>
                    </div>
                    
                    <div className="w-full bg-slate-200 rounded-full h-2">
                      <div
                        className={`h-2 rounded-full ${
                          fillPercentage > 90 ? 'bg-red-500' :
                          fillPercentage > 70 ? 'bg-orange-500' :
                          'bg-blue-500'
                        }`}
                        style={{ width: `${Math.min(fillPercentage, 100)}%` }}
                      />
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <span className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600`}>
                        {Math.round(fillPercentage)}% full
                      </span>
                      <span className={`${isMobile ? 'text-xs' : 'text-sm'} text-slate-600`}>
                        {formatNumber(tank.capacity)}L max
                      </span>
                    </div>

                    {tank.washAlertStatus !== 'ok' && (
                      <div className={`${status.bgColor} rounded p-2 mt-2`}>
                        <p className={`${isMobile ? 'text-xs' : 'text-sm'} font-medium ${status.textColor}`}>
                          Action: {status.action}
                        </p>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

local Base = import 'Base.libsonnet';

local Validations = {
  Combinations:[
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.Y,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.Y,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.Y,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.Y,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.N,
          },
        },
      },
    },
    {
      'if': {
        properties: {
          modified_opinion: {
            const: Base.Const.N,
          },
          other_matters: {
            const: Base.Const.N,
          },
          material_weakness: {
            const: Base.Const.N,
          },
          significiant_deficiency: {
            const: Base.Const.N,
          },          
        },
      },
      'then': {
        properties: {
          other_findings: {
            const: Base.Const.Y,
          },
        },
      },
    },                  
  ],
  PriorReferences: [
    {
      'if': {
        properties: {
          repeat_prior_reference: {
            const: Base.Const.Y,
          },
        },
      },
      'then': {
        required:['prior_references'] 
      },
    },
  ],
};

{
  Validations: Validations,
}
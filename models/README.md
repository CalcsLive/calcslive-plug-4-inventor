# Example Inventor Models

This folder contains sample Inventor files for learning and testing the CalcsLive Plug integration.

## Available Examples

### Coming Soon

Example models will be added here to demonstrate:

- **Basic Parameter Mapping**: Simple part with Length, Width, Height parameters
- **Calculated Parameters**: Part with input and output (calculated) parameters
- **Unit Conversions**: Examples showing mm ↔ inches ↔ meters
- **Complex Assemblies**: Multi-part assemblies with shared parameters
- **Engineering Calculations**: Real-world examples (pressure vessels, beams, etc.)

## How to Use

1. **Open Example Model** in Autodesk Inventor
2. **Start CalcsLive Bridge**: `python main.py` (from project root)
3. **Open CalcsLive Dashboard**: http://localhost:3000/inventor/dashboard
4. **Explore Integration**: Test parameter mapping and synchronization

## Contributing Examples

Have a useful Inventor model that demonstrates CalcsLive integration?

1. Save your model in this folder
2. Add description below
3. Submit pull request

### Guidelines for Example Models

- Keep files small (<5MB preferred)
- Use clear, descriptive parameter names
- Add comments explaining the engineering calculations
- Include a brief description of what the model demonstrates

## File Format

- **Inventor Parts**: `.ipt` files
- **Inventor Assemblies**: `.iam` files (with referenced parts)

---

**Note**: Inventor files should be saved in Inventor 2020+ format for broad compatibility.

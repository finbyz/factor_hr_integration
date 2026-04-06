# FactoHR Integration for ERPNext

Complete integration solution to sync employee data from FactoHR HRMS to ERPNext.

## Features

- ✅ **Automatic Employee Sync** - Sync employee data from FactoHR to ERPNext
- ✅ **Field Mapping** - Maps 15+ fields including personal info, department, designation
- ✅ **Auto-Create** - Automatically creates missing departments and designations
- ✅ **Manual & Scheduled Sync** - Trigger sync manually or schedule hourly/daily/weekly
- ✅ **Comprehensive Logging** - Detailed sync logs with success/failure tracking
- ✅ **Error Handling** - Robust error handling with detailed error messages
- ✅ **Employee Mapping** - Tracks sync status for each employee

## Installation

### 1. Install the App

```bash
cd /path/to/your/bench
bench get-app https://github.com/your-repo/factor_hr_integration
bench --site your-site install-app factor_hr_integration
```

### 2. Run Migrations

```bash
bench --site your-site migrate
```

### 3. Restart Bench

```bash
bench restart
```

## Configuration

### Step 1: Access FactoHR Settings

1. Login to ERPNext
2. Go to **Setup > Integrations > FactoHR Settings**

### Step 2: Configure API Credentials

Fill in the following fields:

| Field | Description | Required |
|-------|-------------|----------|
| **API Endpoint** | FactoHR API base URL (e.g., `https://api.factohr.com`) | Yes |
| **API Key** | Bearer token for authentication | Yes |
| **Default Company** | Default company for new employees | Yes |
| **Enable Auto Sync** | Enable automatic scheduled sync | No |
| **Sync Frequency** | How often to sync (Hourly/Daily/Weekly) | If auto sync enabled |
| **Sync From Date** | Only sync employees from this date onwards | No |
| **Auto Create Missing Departments** | Automatically create departments if not found | No (Default: Yes) |
| **Auto Create Missing Designations** | Automatically create designations if not found | No (Default: Yes) |

### Step 3: Test Connection

1. Click **Test Connection** button
2. Verify successful connection to FactoHR API

### Step 4: Initial Sync

1. Click **Sync Now** button
2. Monitor sync progress and results
3. Check **Sync Logs** section for details

## Field Mapping

The integration maps the following fields from FactoHR to ERPNext:

| FactoHR Field | ERPNext Field | Description |
|---------------|---------------|-------------|
| `EmpCode` | `employee_number` | Unique employee identifier |
| `FirstName` | `first_name` | Employee first name |
| `MiddleName` | `middle_name` | Employee middle name |
| `LastName` | `last_name` | Employee last name |
| `Title` | `salutation` | Mr/Ms/Mrs |
| `DateOfBirth` | `date_of_birth` | Date of birth |
| `JoiningDate` | `date_of_joining` | Date of joining |
| `Gender` | `gender` | Male/Female |
| `Status` | `status` | Active/Left |
| `Mobile` | `cell_number` | Mobile phone number |
| `Email` | `company_email` | Work email address |
| `PersonalEmail` | `personal_email` | Personal email address |
| `Department` | `department` | Employee department |
| `Designation` | `designation` | Employee designation |
| `Manager` | `reports_to` | Reporting manager |

## Usage

### Manual Sync

1. Go to **FactoHR Settings**
2. Click **Sync Now** button
3. Wait for sync to complete
4. Check sync results in the message popup

### Automatic Sync

1. Enable **Auto Sync** in FactoHR Settings
2. Select **Sync Frequency** (Hourly/Daily/Weekly)
3. Save the settings
4. Sync will run automatically based on the schedule

### Monitor Sync Status

1. Check **Sync Logs** table in FactoHR Settings
2. View **FactoHR Employee Mapping** list for individual employee sync status
3. Check **Error Log** for detailed error information

## API Response Format

The integration expects FactoHR API to return data in this format:

```json
{
  "Status": "Success",
  "Message": "37 employees found",
  "Data": [
    {
      "EmployeeData": {
        "EmpCode": "001",
        "FirstName": "John",
        "LastName": "Doe",
        "Email": "john.doe@company.com",
        "Mobile": "9876543210",
        "JoiningDate": "2020-01-01T00:00:00",
        "Status": "Active"
      },
      "CurrentCategoryList": [
        {
          "Category": {
            "CategoryType": {"Type": "Department"},
            "Description": "IT Department"
          }
        },
        {
          "Category": {
            "CategoryType": {"Type": "Designation"},
            "Description": "Software Engineer"
          }
        }
      ]
    }
  ]
}
```

## Troubleshooting

### Common Issues

#### 1. Connection Failed
- **Cause**: Invalid API endpoint or API key
- **Solution**: Verify API credentials in FactoHR Settings

#### 2. Sync Fails with Authentication Error
- **Cause**: API key expired or invalid
- **Solution**: Update API key in FactoHR Settings

#### 3. Employee Creation Failed
- **Cause**: Missing required fields or validation errors
- **Solution**: Check Error Log for specific field issues

#### 4. Department/Designation Not Found
- **Cause**: Auto-create options disabled
- **Solution**: Enable auto-create options or manually create missing records

### Error Logs

Check the following for detailed error information:

1. **FactoHR Settings > Sync Logs** - High-level sync results
2. **FactoHR Employee Mapping** - Individual employee sync status
3. **Error Log** (Setup > System > Error Log) - Detailed technical errors

### Debug Mode

Enable debug logging by adding this to your site config:

```json
{
  "developer_mode": 1,
  "log_level": "DEBUG"
}
```

## API Rate Limits

- The integration respects API rate limits
- Failed requests are logged for manual review
- Consider sync frequency based on your FactoHR API limits

## Data Privacy

- API keys are stored encrypted in the database
- Employee data is synced securely over HTTPS
- No sensitive data is logged in plain text

## Support

For technical support:

1. Check the **Error Log** for specific error messages
2. Review **Sync Logs** for sync statistics
3. Contact your system administrator
4. Raise an issue on the GitHub repository

## Version History

- **v1.0.0** - Initial release with basic employee sync
- **v1.1.0** - Added department and designation auto-creation
- **v1.2.0** - Added scheduled sync and improved error handling

## License

MIT License - see LICENSE file for details.
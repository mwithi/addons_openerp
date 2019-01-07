<!DOCTYPE html>
<html>
<head>
    <style type="text/css">
        ${css}
        
        body {
		    font-size: xx-small;
		}

		table {
		    border-spacing: 0px;
		    page-break-inside: auto;
		    table-layout: fixed;
		}
		
		table tr {
            page-break-inside: avoid; 
            page-break-after: auto;
  		}
  		
  		tr.subtotal td {
  			font-weight: bold;
			font-size: xx-small;
  			line-height: 20px;
			border-top: 1px solid black;
		    border-bottom: 2px solid black;
		}
		
		tr.total td {
  			font-weight: bold;
			font-size: xx-small;
  			line-height: 20px;
			border-top: 1px solid black;
		    border-bottom: double black;
		}
		
		tr.space td {
  			line-height: 20px;
		}
		
		.values {
			font-size: xx-small;
			text-align: right;
		}
		
		.dates {
			text-align: center;
			font-size: xx-small;
		}
		
		.labels {
			font-size: xx-small;
			text-align: left;
			overflow: hidden;
			text-overflow: ellipsis;
			white-space: nowrap;
		}
		
		tr.category td {
			font-size: xx-small;
			line-height: 20px;
			font-weight: bold;
		}
		
		.posted {
			font-size: xx-small;
			text-align: right;
			color: black;
		}
		
		.unposted {
			font-size: xx-small;
			text-align: right;
			color: blue;
		}
		
    </style>
</head>
<body>
    <%page expression_filter="entity"/>
    <br />
    <h1><b><i>Fixed Assets Register (Book Depreciation)</i></b></h1>
    <%
    """
    print "IN REPORT!"
    print objects, dir(objects)
    print "*************** LOCALS:"
    pp(locals())
    print datelines()
    print lines()
    """
    %>

    <table style="width: 100%" border="0">
        <tr class="table_header">
            <td colspan="3" height="30px">
                %for date in datelines():
                    Fiscal Year: ${date['fiscal_year']} (Values: ${date['currency']})
                    <br />
                    Unposted in blue
                %endfor
            </td>
        </tr>
    </table>

    <table style="width: 100%;">
        <tr>
        	<th width="3%" class="labels">ID</th>
            <th width="4%" class="labels">Code</th>
            <th class="labels">Name</th>
            <th width="4%" class="labels">Deprec.<br />Start<br />Date</th>
            <th width="6%" class="values">Opening<br />Value</th>
            <th width="6%" class="values">Increases</th>
            <th width="6%" class="values">Decreases</th>
            <th width="7%" class="values">Gross Book<br />Value</th>
            <th width="6%" class="values">Sales</th>
            <th width="6%" class="values">Profit / (Loss)<br />on Disposal</th>
            <th width="6%" class="values">Accumulated Depreciation<br />Previous Years</th>
            <th width="6%" class="values">Depreciation Current Year</th>
            <th width="6%" class="values">Write off<br />Accumulated Depreciation</th>
            <th width="6%" class="values">Total Depreciation</th>
            <th width="7%" class="values">Net Book<br />Value</th>
        </tr>
        %for line in lines():
        	%if line['type'] == 'category':
	        	<tr class="category">
	        		<td></td>
	    			<td colspan="14">${line['category']}%</td>
	    		</tr>
			%elif line['type'] == 'asset':
				<tr>
	        		<td>${line['id']}</td>
	        		<td>${line['code']}</td>
	        		<td class="labels">${line['asset']}</td>
	        		<td class="dates">${line['date_start']}</td>
	        		<td class="values">${formatLang(line['opening_cost'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['revaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['devaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['gross_book_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['sale_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['profit_loss_disposal'], digits=2, grouping=True)}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%endif
	        		<td class="values">${formatLang(line['write_off_accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['net_value'], digits=2, grouping=True)}</td>
	        	</tr>
        	%elif line['type'] == 'subtotal':
	        	<tr class="subtotal">
	        		<td></td>
	        		<td></td>
	        		<td colspan="2">${line['category']}</td>
	        		<td class="values">${formatLang(line['opening_cost'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['revaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['devaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['gross_book_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['sale_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['profit_loss_disposal'], digits=2, grouping=True)}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%endif
	        		<td class="values">${formatLang(line['write_off_accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['net_value'], digits=2, grouping=True)}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%elif line['type'] == 'total':
	        	<tr class="total">
	        		<td></td>
	        		<td>Total</td>
	        		<td></td>
					<td></td>
	        		<td class="values">${formatLang(line['opening_cost'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['revaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['devaluation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['gross_book_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['sale_value'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['profit_loss_disposal'], digits=2, grouping=True)}</td>
	        		%if line['previous_posted']:
	        			<td class="values">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['accumulated_depreciation_previous_years'], digits=2, grouping=True)}</td>
	        		%endif
	        		%if line['current_posted']:
	        			<td class="values">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%else:
	        			<td class="unposted">${formatLang(line['depreciation_current_year'], digits=2, grouping=True)}</td>
	        		%endif
	        		<td class="values">${formatLang(line['write_off_accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['accumulated_depreciation'], digits=2, grouping=True)}</td>
	        		<td class="values">${formatLang(line['net_value'], digits=2, grouping=True)}</td>
	        	</tr>
	        	<tr class="space"><td colspan="13">&nbsp</td></tr>
    		%endif
        %endfor
    </table>
</body>
</html>
